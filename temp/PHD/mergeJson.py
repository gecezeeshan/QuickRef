import json
import re

# === File paths ===
json_file = "finalProfWithEmail.json"
log_file = "logs1.txt"

# === Load logs and extract successfully sent emails ===
with open(log_file, "r", encoding="utf-8") as f:
    log_lines = f.readlines()

# Only capture lines that say: Email sent to Name (email) ...
email_pattern = re.compile(r"Email sent to .* \(([^)]+)\)")
sent_emails = set()

for line in log_lines:
    match = email_pattern.search(line)
    if match:
        sent_emails.add(match.group(1).strip().lower())

# === Load JSON ===
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# === Update IsEmailSend flag ===
updated_count = 0
for country, universities in data.items():
    for university, faculty_list in universities.items():
        for prof in faculty_list:
            prof_email = prof.get("email", "").strip().lower()
            if prof_email in sent_emails:
                if not prof.get("IsEmailSend", False):
                    prof["IsEmailSend"] = True
                    updated_count += 1

# === Save updated JSON ===
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Updated IsEmailSend=True for {updated_count} professors.")
