import requests
import re
import csv
import os
from datetime import datetime, timezone

SHARE_URL = "https://contentrewards.com/share/YTQwZTI0MzEtOTEzZi00OWIxLTg1MGYtNDZlOTMxMDg0ODZm.YRgvVMKWQTFr"
CSV_FILE = "data.csv"

def parse_number(text):
    """Convert '801.8K' or '1.2K' or '367' to integer."""
    text = text.strip()
    if 'K' in text:
        return int(float(text.replace('K', '')) * 1000)
    elif 'M' in text:
        return int(float(text.replace('M', '')) * 1_000_000)
    else:
        return int(text.replace(',', ''))

def scrape():
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(SHARE_URL, headers=headers, timeout=15)
    html = resp.text

    # Extract stats from the HTML
    views    = re.search(r'Views\s*</[^>]+>\s*([\d.,KM]+)', html)
    likes    = re.search(r'Likes\s*</[^>]+>\s*([\d.,KM]+)', html)
    comments = re.search(r'Comments\s*</[^>]+>\s*([\d.,KM]+)', html)
    shares   = re.search(r'Shares\s*</[^>]+>\s*([\d.,KM]+)', html)
    payouts  = re.search(r'Payouts\s*</[^>]+>\s*\$([\d.,]+)', html)
    approved = re.search(r'Approved\s*</[^>]+>\s*(\d+)of', html)

    row = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
        "views":     parse_number(views.group(1))    if views    else "",
        "likes":     parse_number(likes.group(1))    if likes    else "",
        "comments":  parse_number(comments.group(1)) if comments else "",
        "shares":    parse_number(shares.group(1))   if shares   else "",
        "payouts":   payouts.group(1)                if payouts  else "",
        "approved":  approved.group(1)               if approved else "",
    }

    print(f"Scraped: {row}")

    # Write header if file doesn't exist
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

if __name__ == "__main__":
    scrape()
