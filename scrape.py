import csv
import os
import re
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
 
SHARE_URL = "https://contentrewards.com/share/YTQwZTI0MzEtOTEzZi00OWIxLTg1MGYtNDZlOTMxMDg0ODZm.YRgvVMKWQTFr"
CSV_FILE = "data.csv"
 
def parse_number(text):
    text = text.strip().replace(',', '')
    if 'K' in text:
        return int(float(text.replace('K', '')) * 1000)
    elif 'M' in text:
        return int(float(text.replace('M', '')) * 1_000_000)
    else:
        return int(text)
 
def scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(SHARE_URL, wait_until="networkidle", timeout=30000)
        html = page.content()
        browser.close()
 
    def find(pattern):
        m = re.search(pattern, html)
        return m.group(1).strip() if m else ""
 
    views    = find(r'Views</\w+>\s*([\d.,KM]+)')
    likes    = find(r'Likes</\w+>\s*([\d.,KM]+)')
    comments = find(r'Comments</\w+>\s*([\d.,KM]+)')
    shares   = find(r'Shares</\w+>\s*([\d.,KM]+)')
    payouts  = find(r'\$([\d.,]+)\s*</\w+>\s*Approved')
    approved = find(r'(\d+)\s*of \d+ total')
 
    row = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
        "views":     parse_number(views)    if views    else "",
        "likes":     parse_number(likes)    if likes    else "",
        "comments":  parse_number(comments) if comments else "",
        "shares":    parse_number(shares)   if shares   else "",
        "payouts":   payouts,
        "approved":  approved,
    }
 
    print(f"Scraped: {row}")
 
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
 
if __name__ == "__main__":
    scrape()
