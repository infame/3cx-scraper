from pathlib import Path
from bs4 import BeautifulSoup

# HTML cache file
cache_file = Path("html_cache/AE_RK_.html")

# Check if the file exists
if not cache_file.exists():
    print(f"File {cache_file} not found!")
    exit(1)

# Read the file content
with cache_file.open("r", encoding="utf-8") as file:
    html_content = file.read()

# Parse HTML using BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Print partner level headers
h3_tags = soup.find_all("h3")
for h3 in h3_tags:
    print(f"Partner Level: {h3.get_text(' ', strip=True)}")

# Find all partner cards
partner_boxes = soup.find_all("div", class_="xcx_partner_box")

for box in partner_boxes:
    # Company name
    company_name_elem = box.find("a")
    company_name = company_name_elem.find("strong").get_text(strip=True) if company_name_elem else "Unknown"

    # Extract flex-blocks (divs with inline style "display:flex")
    flex_divs = box.find_all("div", style=lambda value: value and "display:flex" in value)

    if len(flex_divs) >= 4:
        # First flex-block: phone number
        telephone = flex_divs[0].get_text(strip=True)
        # Second flex-block: website
        website = flex_divs[1].get_text(strip=True)
        # Third flex-block: address
        address = flex_divs[2].get_text(strip=True)
        # Fourth flex-block: Partner ID (remove extra text)
        partner_id_text = flex_divs[3].get_text(strip=True)
        partner_id = partner_id_text.replace("Partner ID:", "").strip()
    else:
        telephone = website = address = partner_id = "N/A"

    print(f"""
    Company: {company_name}
    Telephone: {telephone}
    Website: {website}
    Address: {address}
    Partner ID: {partner_id}
    """)

print("Parsing completed!")