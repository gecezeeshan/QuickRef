import json
from collections import defaultdict

# Load data from your JSON file
filename = "faculty_with_emails.json"
with open(filename, "r", encoding="utf-8") as file:
    data = json.load(file)

# Organize by country > university > professors (with valid emails)
organized = defaultdict(lambda: defaultdict(list))

for entry in data:
    country = entry.get("country", "")
    university = entry.get("university", "")
    for faculty in entry.get("faculty", []):
        email = faculty.get("email", "")
        if email and "@" not in email:
            organized[country][university].append({
                "name": faculty.get("name", ""),
                "link": faculty.get("link", ""),
                "email": email
            })

# Convert defaultdict to normal dict for saving
organized_dict = {country: dict(unis) for country, unis in organized.items()}

# Output result
with open("noemail_professors.json", "w", encoding="utf-8") as out_file:
    json.dump(organized_dict, out_file, indent=2)

# Optional: print to console
print(json.dumps(organized_dict, indent=2))
