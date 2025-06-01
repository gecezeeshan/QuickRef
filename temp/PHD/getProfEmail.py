import json
import re
import requests
from bs4 import BeautifulSoup
import time
import smtplib
from email.message import EmailMessage
from urllib.parse import urljoin

# === SETTINGS ===
EMAIL_AT_END = False
RECIPIENT = "gecezeeshan@gmail.com"
START_FROM = 0

def normalize_email(obfuscated_email):
    email = obfuscated_email.lower()
    email = email.replace('[at]', '@').replace('(at)', '@').replace(' at ', '@').replace('{at}', '@')
    email = email.replace('[dot]', '.').replace('(dot)', '.').replace(' dot ', '.').replace('{dot}', '.')
    email = re.sub(r'\s+', '', email)
    return email

def extract_email(text, name_parts):
    text = text.lower()
    patterns = [
        r"[a-zA-Z0-9._%+-]+\s*(\[at\]|\(at\)| at |{at})\s*[a-zA-Z0-9.-]+\s*(\[dot\]|\(dot\)| dot |{dot}|\.)\s*[a-zA-Z]{2,}",
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return normalize_email(match.group())

    for part in name_parts:
        match = re.search(rf"{part}[a-z0-9]*\s*(\[at\]|\(at\)| at |{at})\s*[a-zA-Z0-9.-]+", text)
        if match:
            return normalize_email(match.group())
    return None

def find_contact_page(soup, base_url):
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].lower()
        if "contact" in href:
            return urljoin(base_url, a_tag["href"])
    return None

# === LOAD DATA ===
with open("professors_with_noemail.json", "r", encoding="utf-8") as f:
    data = json.load(f)

processed_count = 0
for country in data:
    for university in data[country]:
        for person in data[country][university]:
            if processed_count < START_FROM:
                processed_count += 1
                continue

            name = person.get("name", "")
            name_parts = name.lower().split()
            url = person.get("link")

            print(f"[{processed_count}] → {name} | {url}")
            try:
                response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(response.text, "html.parser")
                text = soup.get_text()
                email = extract_email(text, name_parts)

                if not email:
                    contact_url = find_contact_page(soup, url)
                    if contact_url:
                        print(f"🔎 Searching contact page: {contact_url}")
                        try:
                            contact_response = requests.get(contact_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                            contact_text = BeautifulSoup(contact_response.text, "html.parser").get_text()
                            email = extract_email(contact_text, name_parts)
                        except Exception as e:
                            print(f"     ⚠️  Error loading contact page: {e}")

                person["email"] = email if email else ""
                print(f"     ✅ Found: {email}")
            except Exception as e:
                print(f"     ❌ Error: {e}")
                person["email"] = ""

            processed_count += 1

            if processed_count % 10 == 0:
                with open("professors_with_noemail.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print("💾 Partial save complete.")



with open("professors_with_noemail.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("🎉 All done. Total processed:", processed_count)
