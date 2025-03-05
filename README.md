# 3CX Partner Scraper

## Quick Start

1. Install dependencies (if not installed):
   ```sh
   pip install -r requirements.txt
   ```

2. Prepare a CSV file with locations (example: `locations.csv`).

3. Run the scraper:
   ```sh
   python script.py -i locations.csv -o partners.csv
   ```

4. The scraped partners will be saved in `partners.csv`.  
   Done.

**PS:** Uses cache for repeated runs.