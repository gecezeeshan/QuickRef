import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# === CONFIGURATION ===
your_email = "gecezeeshan@gmail.com"
your_password = "iwuhqidohtnatnjr"  # App password
subject = "Prospective PhD Student Inquiry – Syed Zeeshan Ali"
json_file = "FinalProfWithEmail.json"
attachments = ["MasterTranscript.pdf", "Senior_Software_Consultant_Resume.pdf"]
target_countries = {"Canada", "United States","South Korea","Austria","Germany","Switzerland","United Kingdom","France","Italy","Spain","Netherlands","Belgium","Sweden",
                    "Norway","Finland","Denmark","Ireland","Poland","Czech Republic","Hungary","Portugal","Greece","Turkey","Russia","Ukraine"}

#target_countries = {"Germany"}

# Load email template (with "Dear Professor," to be replaced)
with open("email.txt", "r", encoding="utf-8") as f:
    email_template = f.read()

# Load professor data
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Setup SMTP
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(your_email, your_password)

# Email each professor in target countries
for country in data:
    if country not in target_countries:
        continue

    for university in data[country]:
        for prof in data[country][university]:
            email = prof.get("email", "").strip()
            name = prof.get("name", "Professor").strip()
            already_sent = prof.get("IsEmailSend", False)

            if email and not already_sent:
                try:
                    # Personalize the message
                    personalized_body = email_template.replace("Dear Professor", f"Dear {name}")

                    msg = MIMEMultipart()
                    msg["From"] = your_email
                    msg["To"] = email
                    msg["Subject"] = subject
                    msg.attach(MIMEText(personalized_body, "plain"))

                    for file_path in attachments:
                        part = MIMEBase("application", "octet-stream")
                        with open(file_path, "rb") as attachment:
                            part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename= {file_path}")
                        msg.attach(part)

                    server.sendmail(your_email, email, msg.as_string())
                    print(f"✅ Email sent to {name} ({email}) at {university}, {country}")
                    prof["IsEmailSend"] = True  # Mark as sent

                    # Immediately save the updated JSON after sending
                    with open(json_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)


                except Exception as e:
                    print(f"❌ Failed to send to {email}: {e}")

# Save updated JSON
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

server.quit()
print("📩 Done: Personalized emails sent to professors.")
