import asyncio
import aiohttp
import csv
import os
import sys
import time
from typing import Dict, Any, List, Tuple, Optional
from collections import deque

# ---------------------------
# CONFIG (edit these)
# ---------------------------
WABA_BASE_URL = os.environ.get("WABA_BASE_URL", "https://your-waba-host:port/v2")
# On-Premises example path: POST /contacts
# Docs: https://developers.facebook.com/docs/whatsapp/on-premises/reference/contacts/

WABA_TOKEN = os.environ.get("WABA_TOKEN", "REPLACE_WITH_BEARER_TOKEN")
# Auth: typically "Authorization: Bearer <token>"

REQUEST_TIMEOUT = 30
CONCURRENT_REQUESTS = 32       # Tune based on your infra and BSP guidance
BATCH_SIZE = 50                # Many BSPs accept up to 50 numbers per /contacts call
MAX_RETRIES = 6
INITIAL_BACKOFF = 1.0
MAX_BACKOFF = 30.0

# CSV tuning
READ_CHUNK_ROWS = 100_000      # Number of rows ingested before flushing to writer
OUTPUT_STATUS_COLUMN = "wa_status"  # exists | non_exist | error

# ---------------------------
# Utility: exponential backoff
# ---------------------------
def _next_backoff(attempt: int) -> float:
    return min(MAX_BACKOFF, INITIAL_BACKOFF * (2 ** attempt))

# ---------------------------
# Contacts API call (On-Prem)
# ---------------------------
async def check_contacts(session: aiohttp.ClientSession, numbers: List[str]) -> Dict[str, str]:
    """
    Returns map: number -> 'exists'|'non_exist'|'error'
    Expected payload for On-Prem /contacts:
      { "blocking": "wait", "contacts": ["<E164>", ...] }
    Response example includes status per number; map to exists/non_exist.
    """
    url = f"{WABA_BASE_URL}/contacts"
    payload = {
        "blocking": "wait",
        "contacts": numbers
    }
    headers = {
        "Authorization": f"Bearer {WABA_TOKEN}",
        "Content-Type": "application/json"
    }

    attempt = 0
    while True:
        try:
            async with session.post(url, json=payload, timeout=REQUEST_TIMEOUT, headers=headers) as resp:
                if resp.status in (429, 502, 503, 504):
                    # Throttled or transient errors
                    backoff = _next_backoff(attempt)
                    attempt += 1
                    await asyncio.sleep(backoff)
                    continue
                if resp.status >= 400:
                    # Permanent error — mark as 'error'
                    # (We could parse body to differentiate)
                    return {n: "error" for n in numbers}

                data = await resp.json()
                # Expected structure (simplified): {"contacts":[{"input":"<num>","status":"valid"/"invalid"/ ...}]}
                out = {}
                for c in data.get("contacts", []):
                    num = c.get("input")
                    status = c.get("status", "").lower()
                    if status in ("valid", "processing", "pending"):  # 'processing' shouldn't happen with blocking=wait
                        out[num] = "exists"
                    elif status in ("invalid", "failed"):
                        out[num] = "non_exist"
                    else:
                        out[num] = "error"
                # Any missing numbers default to error
                for n in numbers:
                    if n not in out:
                        out[n] = "error"
                return out

        except (aiohttp.ClientError, asyncio.TimeoutError):
            backoff = _next_backoff(attempt)
            attempt += 1
            if attempt > MAX_RETRIES:
                return {n: "error" for n in numbers}
            await asyncio.sleep(backoff)

# ---------------------------
# Producer/Consumer pipeline
# ---------------------------
async def worker(name: int,
                 session: aiohttp.ClientSession,
                 queue: "asyncio.Queue[Tuple[int, List[Tuple[int, Dict[str, Any]]]]]",
                 results: Dict[int, str]):
    """Consumes batches from queue, calls /contacts, stores results by row_index."""
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            return
        batch_id, batch_rows = item
        numbers = [row["__wa_number"] for _, row in batch_rows]
        mapping = await check_contacts(session, numbers)
        # Place results keyed by global row index
        for (idx, row) in batch_rows:
            num = row["__wa_number"]
            results[idx] = mapping.get(num, "error")
        queue.task_done()

def normalize_number(raw: str) -> Optional[str]:
    """Minimal cleanup to E.164-ish digits. You can plug libphonenumber here for strictness."""
    digits = "".join(ch for ch in (raw or "") if ch.isdigit() or ch == '+')
    if not digits:
        return None
    if digits[0] != '+':
        # naive: if starts with 00, convert to +
        if digits.startswith("00"):
            digits = '+' + digits[2:]
        # else assume already E164 without + (not ideal). Better: use country defaults or libphonenumber.
        else:
            digits = '+' + digits
    return digits

async def process_csv(input_path: str, number_column: str, output_path: str):
    # We keep a rolling output writer that flushes every READ_CHUNK_ROWS
    # We also keep an in-memory results map of row_index -> status
    # To preserve order, we write rows in sequence as soon as their status is available.
    pending_rows: deque = deque()  # items are (row_index, row_dict)
    results: Dict[int, str] = {}
    next_to_write = 0
    total = 0

    connector = aiohttp.TCPConnector(limit=CONCURRENT_REQUESTS)
    async with aiohttp.ClientSession(connector=connector) as session:
        queue: "asyncio.Queue[Tuple[int, List[Tuple[int, Dict[str, Any]]]]]" = asyncio.Queue(maxsize=CONCURRENT_REQUESTS * 2)

        # Launch workers
        workers = [asyncio.create_task(worker(i, session, queue, results)) for i in range(CONCURRENT_REQUESTS)]

        # Prepare CSV IO
        with open(input_path, "r", newline="", encoding="utf-8-sig") as f_in, \
             open(output_path, "w", newline="", encoding="utf-8") as f_out:
            reader = csv.DictReader(f_in)
            fieldnames = list(reader.fieldnames or [])
            if OUTPUT_STATUS_COLUMN not in fieldnames:
                fieldnames.append(OUTPUT_STATUS_COLUMN)
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            batch: List[Tuple[int, Dict[str, Any]]] = []
            batch_id = 0

            for row in reader:
                row_index = total
                total += 1
                raw_num = row.get(number_column)
                norm = normalize_number(raw_num)
                # stash number for the validator
                row["__wa_number"] = norm if norm else ""

                pending_rows.append((row_index, row))
                batch.append((row_index, row))

                if len(batch) >= BATCH_SIZE:
                    await queue.put((batch_id, batch))
                    batch = []
                    batch_id += 1

                # Drain writer if we have many pending rows to limit memory
                if len(pending_rows) >= READ_CHUNK_ROWS:
                    next_to_write = _drain_ready(pending_rows, results, writer, next_to_write)

            # Flush last partial batch
            if batch:
                await queue.put((batch_id, batch))

            # Signal termination to workers
            for _ in workers:
                await queue.put(None)

            await queue.join()

            # Final drain
            _ = _drain_ready(pending_rows, results, writer, next_to_write, final=True)

        # Cancel workers if any are still alive
        for w in workers:
            if not w.done():
                w.cancel()

    print(f"Processed {total:,} rows into {output_path}")

def _drain_ready(pending_rows: deque, results: Dict[int, str], writer: csv.DictWriter, next_to_write: int, final: bool=False):
    """
    Writes rows in input order whenever their status is ready.
    Preserves all input columns; adds OUTPUT_STATUS_COLUMN.
    """
    while pending_rows and (final or pending_rows[0][0] in results):
        row_index, row = pending_rows[0]
        if row_index not in results:
            break
        status = results[row_index]
        # Clean aux field
        wa_num = row.pop("__wa_number", None)
        row[OUTPUT_STATUS_COLUMN] = status if wa_num else "error"  # empty/invalid number -> error
        writer.writerow(row)
        pending_rows.popleft()
        next_to_write += 1
    return next_to_write

def main():
    if len(sys.argv) < 4:
        print("Usage: python wa_validator.py <input.csv> <number_column_name> <output.csv>")
        sys.exit(1)
    input_csv = sys.argv[1]
    number_col = sys.argv[2]
    output_csv = sys.argv[3]

    # Basic checks
    if not os.path.exists(input_csv):
        print(f"Input not found: {input_csv}")
        sys.exit(2)

    start = time.time()
    asyncio.run(process_csv(input_csv, number_col, output_csv))
    dur = time.time() - start
    print(f"Done in {dur:.1f}s")

if __name__ == "__main__":
    main()
