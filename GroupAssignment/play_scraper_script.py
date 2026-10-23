import csv
import re
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

#Instructions: open Tor Browser, connect to the network, and minimize the window and run this script

# Base onion URL derived from the site's pagination JS function (index.php?page=N)
BASE_URL = "http://j75o7xvvsm4lpsjhkjvb4wl2q6ajegvabe6oswthuaubbykk4xkzgpid.onion/index.php"
OUTPUT_CSV = "play_victims_all_pages.csv"

# Port 9150 is default for Tor Browser.
# (If using system Tor service via 'sudo systemctl start tor', change port to 9050)
PROXIES = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
}

# Date filter bounds (Jan 1, 2026 - Sep 30, 2026)
START_DATE = datetime(2026, 1, 1)
END_DATE = datetime(2026, 9, 30, 23, 59, 59)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; RV:109.0) Gecko/20100101 Firefox/115.0'
}

def parse_card(card):
    """Parses individual <th class="News"> victim cards."""
    victim_name = card.contents[0].strip() if card.contents else "Unknown"
    text_content = card.get_text(separator=' ', strip=True)

    # Location / Country
    loc_icon = card.find('i', class_='location')
    country = loc_icon.next_sibling.strip() if loc_icon and loc_icon.next_sibling else "N/A"

    # Website Link
    link_icon = card.find('i', class_='link')
    website = link_icon.next_sibling.strip() if link_icon and link_icon.next_sibling else "N/A"

    # View Counter
    views_match = re.search(r'views:\s*(\d+)', text_content)
    views = views_match.group(1) if views_match else "0"

    # Dates
    added_match = re.search(r'added:\s*(\d{4}-\d{2}-\d{2})', text_content)
    added_date = added_match.group(1) if added_match else ""

    pub_match = re.search(r'publication date:\s*(\d{4}-\d{2}-\d{2})', text_content)
    pub_date = pub_match.group(1) if pub_match else ""

    # Status Banner
    status_h = card.find('h')
    status = status_h.get_text(strip=True) if status_h else "N/A"

    return {
        'ransomware_group': 'Play',
        'victim_name': victim_name,
        'country': country,
        'website': website,
        'added_date': added_date,
        'publication_date': pub_date,
        'views': views,
        'status': status
    }

def scrape_all_pages(total_pages=21):
    session = requests.Session()
    session.proxies.update(PROXIES)
    session.headers.update(HEADERS)

    all_records = []

    for page_num in range(1, total_pages + 1):
        url = f"{BASE_URL}?page={page_num}"
        print(f"[+] Fetching Page {page_num}/{total_pages}: {url}")

        max_retries = 3
        html_content = None

        # Robust retry handling to handle Tor network blips
        for attempt in range(1, max_retries + 1):
            try:
                response = session.get(url, timeout=30)
                if response.status_code == 200:
                    html_content = response.text
                    break
                else:
                    print(f"  [!] HTTP {response.status_code} on attempt {attempt}")
            except requests.RequestException as e:
                print(f"  [!] Connection/Timeout error on attempt {attempt}: {e}")
                time.sleep(3)

        if not html_content:
            print(f"  [-] Failed to retrieve Page {page_num} after {max_retries} attempts. Skipping...")
            continue

        soup = BeautifulSoup(html_content, 'html.parser')
        cards = soup.find_all('th', class_='News')
        print(f"  [✓] Found {len(cards)} cards on Page {page_num}.")

        added_on_page = 0
        for card in cards:
            record = parse_card(card)

            # Date Filtering logic
            filter_date = record['publication_date'] or record['added_date']
            if filter_date:
                try:
                    dt = datetime.strptime(filter_date, '%Y-%m-%d')
                    if not (START_DATE <= dt <= END_DATE):
                        continue
                except ValueError:
                    pass

            all_records.append(record)
            added_on_page += 1

        print(f"  [->] Added {added_on_page} target records from Page {page_num}.")
        
        # Friendly delay between onion page requests
        time.sleep(1.5)

    # Save final structured data to CSV
    fieldnames = ['ransomware_group', 'victim_name', 'country', 'website', 'added_date', 'publication_date', 'views', 'status']
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)

    print(f"\n[★] Done! Total {len(all_records)} records saved to '{OUTPUT_CSV}'.")

if __name__ == '__main__':
    scrape_all_pages(total_pages=21)
