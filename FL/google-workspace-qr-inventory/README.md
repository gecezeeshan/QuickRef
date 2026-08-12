# Google Workspace QR Inventory (Forms + Sheets + Drive + Apps Script)

A self-contained inventory workflow built **entirely** in Google Workspace.
- **Intake** and **Withdrawal** via Google Forms (each form displays a QR code).
- **Real-time inventory** updates in a master Google Sheet from form submissions.
- **Negative stock protection**: withdrawal checks on-hand and blocks updates with alerts if it would go below 0.
- **Auto views**: live breakdown by **Job Number** and **Subcontractor** using formulas.
- **Document capture (Intake)**: file upload (BOL, packing slip, etc.) stored in Drive folder structure and **linked back** to the transaction row.
- **All code annotated** for easy in-house maintenance.

> Stack: Google Apps Script (native), Google Forms, Google Sheets, Google Drive. Optional use with `clasp` for versioning.

---

## Quick Start

1. **Create a new Apps Script project** (or use `clasp` with this repo) and copy the contents of `/src` and `appsscript.json` into it.
2. Open `src/Config.gs` and set your `ADMIN_EMAIL` (alert recipient). You can leave other IDs blank initially.
3. In the Apps Script editor, run `Setup.install()` **once**. It will:
   - Create the **Master Inventory** spreadsheet with required tabs and formulas.
   - Create **Intake Form** (with file upload) and **Withdrawal Form**; embed QR codes in both.
   - Create labeled **Drive folders** for document storage.
   - Set up **installable triggers** for each form to process submissions.
   - Write back all IDs into the **Config** sheet for future use.
4. After install, open the **Master Inventory** sheet to see:
   - `Transactions` (all form submissions; intake positive, withdrawal negative).
   - `Inventory` (live on-hand).
   - `ByJobNumber` and `BySubcontractor` (live views).
5. Test by submitting the forms via the QR code or the links printed in **Logs** after `Setup.install()`.
6. (Optional) Use `Setup.rebuildQR()` if you ever copy/move forms and need to refresh the QR image.

> ⚠️ **Note on blocking negative stock:** Google Forms cannot prevent a submit at runtime, but the script will **block the inventory update** and write the attempt into an `Exceptions` tab while emailing `ADMIN_EMAIL` with details. No stock is subtracted when insufficient quantity exists.

---

## Sheets Layout

- **Transactions** (append-only audit log)
  - Timestamp, Type (`Intake` | `Withdrawal`), ItemCode, Qty, JobNumber, Subcontractor, FileLinks (for Intake), EditorEmail
- **Inventory** (live on-hand by ItemCode)
  - Uses `QUERY`/`SUMIF` over `Transactions` to compute running totals.
- **ByJobNumber** (live view)
  - Aggregates totals by ItemCode, JobNumber.
- **BySubcontractor** (live view)
  - Aggregates totals by ItemCode, Subcontractor.
- **Config** (IDs and settings written by Setup)

---

## File Upload Routing

Intake Form's upload question places files into a Form-managed folder. The script **moves** the files into your own folder structure:

```
Drive Root/
  Inventory-Docs/ (created by Setup)
    Intake/
      {YYYY}/{MM}/{DD}/
        {JobNumber}/
          {Subcontractor}/
            <files>
```

A link to each file is written back to the corresponding `Transactions` row.

---

## Negative Stock Protection

On **Withdrawal** submit:
- The script checks current on-hand (from `Inventory` calculation) and the requested quantity.
- If insufficient, the transaction is placed into **Exceptions**, email alert is sent, and the `Transactions` row is **not** appended.
- If sufficient, the withdrawal is recorded (negative quantity) and on-hand updates immediately.

---

## Commands

- `Setup.install()` — First-time install (creates Sheets, Forms, folders, and triggers).
- `Setup.rebuildQR()` — Recreates QR images on the forms (if URLs changed).
- `Setup.resetDemo()` — Clears transactions and sample data (keeps structure).
- `OnSubmit.handleIntake_(e)` — Trigger target for Intake Form submissions.
- `OnSubmit.handleWithdrawal_(e)` — Trigger target for Withdrawal Form submissions.

---

## Notes

- **Permissions:** The script will prompt for Drive/Forms/Sheets/Gmail scopes. Form **file upload** requires same Google Workspace domain.
- **AppSheet:** You can later wire AppSheet to the `Transactions`/`Inventory` sheets if you need mobile UX; current solution is Forms-native.
- **Maintenance:** All code has comments; see `docs/Hand-off.md` for a structured walkthrough.
- **Walkthrough:** Record a quick Loom/Meet showing how to scan a QR, submit, and watch the `Inventory` update.

---

## License

MIT
