#!/usr/bin/env python3
import os
import re
import csv
import time
import argparse
import requests
from typing import List, Optional
from bs4 import BeautifulSoup


class Location:
    """Represents a location for partner search."""
    def __init__(self, country: str, country_code: str, region: str, region_code: str, city: Optional[str] = None):
        self.country = country
        self.country_code = country_code
        self.region = region
        self.region_code = region_code
        self.city = city

    def __str__(self) -> str:
        if self.city:
            return f"{self.country} - {self.region} - {self.city}"
        return f"{self.country} - {self.region}"


class Partner:
    """Represents a 3CX partner."""
    def __init__(self, country: str, state: str, city: Optional[str], partner_level: str,
                 company_name: str, telephone: str, website: str, address: str, partner_id: str):
        self.country = country
        self.state = state
        self.city = city
        self.partner_level = partner_level
        self.company_name = company_name
        self.telephone = telephone
        self.website = website
        self.address = address
        self.partner_id = partner_id

    def to_csv_row(self) -> List[str]:
        """Converts a partner into a CSV row."""
        return [
            self.country,
            self.state,
            self.city or "",
            self.partner_level,
            self.company_name,
            self.telephone,
            self.website,
            self.address,
            self.partner_id
        ]


def read_locations_from_csv(filename: str) -> List[Location]:
    """Reads locations from a CSV file."""
    locations = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        # Skip header
        next(reader)
        for row in reader:
            if len(row) < 4:
                continue
            country = row[0]
            country_code = row[1]
            region = row[2]
            region_code = row[3]
            city = row[4] if len(row) > 4 and row[4] else None
            locations.append(Location(country, country_code, region, region_code, city))
    return locations


def get_cache_filename(location: Location, cache_dir: str) -> str:
    """Returns the cache filename for HTML storage."""
    city_part = f"_{location.city.replace(' ', '_')}" if location.city else "_"
    filename = f"{location.country_code}_{location.region_code}{city_part}.html"
    return os.path.join(cache_dir, filename)


def read_cached_html(filename: str) -> Optional[str]:
    """Reads cached HTML from a file."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except (IOError, FileNotFoundError):
        return None


def save_cached_html(filename: str, html: str) -> None:
    """Saves HTML to a cache file."""
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html)


def fetch_html(location: Location, include_headers: bool) -> str:
    """Sends a request to the 3CX API and returns the HTML response."""
    url = "https://www.3cx.com/resellers/xcx-get-partners/"
    # Prepare form data
    form_data = {
        "country": location.country_code,
        "state": location.region_code,
        "name": ""
    }
    if location.city:
        form_data["city"] = location.city

    # Prepare headers
    headers = {}
    if include_headers:
        headers = {
            "accept": "/",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.3cx.com",
            "pragma": "no-cache",
            "referer": "https://www.3cx.com/ordering/find-reseller/",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest"
        }

    response = requests.post(url, data=form_data, headers=headers)
    response.raise_for_status()
    return response.text


def parse_partners_from_html(html: str, location: Location) -> List[Partner]:
    """Parses HTML and extracts partner information."""
    soup = BeautifulSoup(html, "html.parser")
    partners = []

    # Find all partner level headers
    h3_tags = soup.find_all("h3")
    for h3 in h3_tags:
        # Extract partner level (removing <img>)
        partner_level_text = h3.get_text(" ", strip=True)
        level_match = re.search(r"3CX\s+([\w\s]+)\s+Partners", partner_level_text)
        partner_level = level_match.group(1) + " Partners" if level_match else "Unknown"

        # Find the container with partners below the header
        partner_container = h3.find_next("div", class_="xcx_partner_category_row")
        if not partner_container:
            continue

        # Find all partner boxes
        partner_boxes = partner_container.find_all("div", class_="xcx_partner_box")
        for box in partner_boxes:
            # Company name
            company_name_elem = box.find("a")
            company_name = (company_name_elem.find("strong").get_text(strip=True)
                            if company_name_elem else "Unknown")
            # Extract all flex blocks (with inline style "display:flex")
            flex_divs = box.find_all("div", style=lambda value: value and "display:flex" in value)
            if len(flex_divs) >= 4:
                telephone = flex_divs[0].get_text(strip=True)
                website = flex_divs[1].get_text(strip=True)
                address = flex_divs[2].get_text(strip=True)
                partner_id_text = flex_divs[3].get_text(strip=True)
                partner_id = partner_id_text.replace("Partner ID:", "").strip()
            else:
                telephone = website = address = partner_id = ""

            partner = Partner(
                country=location.country,
                state=location.region,
                city=location.city,
                partner_level=partner_level,
                company_name=company_name,
                telephone=telephone,
                website=website,
                address=address,
                partner_id=partner_id
            )
            partners.append(partner)
    return partners


def get_partners_with_cache(location: Location, include_headers: bool, cache_dir: str, use_cache: bool) -> List[Partner]:
    """Gets partners using cached HTML responses when available."""
    cache_file = get_cache_filename(location, cache_dir)
    html_content = None

    # Check for cache
    if use_cache:
        html_content = read_cached_html(cache_file)
        if html_content:
            print(f"[cached for] {location}")

    # If no cache, fetch HTML
    if not html_content:
        try:
            html_content = fetch_html(location, include_headers)
            time.sleep(0.5)
            print(f"[NOT CACHED for] {location}")
            save_cached_html(cache_file, html_content)
            print(f"[SAVE for] {cache_file}")
        except Exception as e:
            print(f"Error fetching HTML for {location}: {str(e)}")
            return []

    return parse_partners_from_html(html_content, location)


def main():
    parser = argparse.ArgumentParser(description="3CX Partner Scraper")
    parser.add_argument("-i", "--input", default="locations.csv", help="Input CSV file with locations")
    parser.add_argument("-o", "--output", default="partners.csv", help="Output CSV file for partners")
    parser.add_argument("--headers", action="store_true", default=True, help="Include headers in HTTP request")
    parser.add_argument("--cache", default="html_cache", help="Directory for storing cached HTML responses")
    parser.add_argument("--use-cache", action="store_true", default=True, help="Use cached HTML responses")
    args = parser.parse_args()

    os.makedirs(args.cache, exist_ok=True)

    try:
        locations = read_locations_from_csv(args.input)
    except Exception as e:
        print(f"Error reading locations: {str(e)}")
        return

    with open(args.output, 'w', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["Country", "State", "City", "Partner Level", "Company Name", "Telephone", "Website", "Address", "Partner ID"])
        for location in locations:
            partners = get_partners_with_cache(location, args.headers, args.cache, args.use_cache)
            for partner in partners:
                writer.writerow(partner.to_csv_row())

    print(f"Done! Partners saved to {args.output}")


if __name__ == "__main__":
    main()