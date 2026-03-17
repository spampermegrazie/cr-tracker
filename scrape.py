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

    def find(label):
        pattern = rf'{label}</span>.*?<span[^>]*>([\d.,KM]+)</span>'
        m = re.search(pattern, html, re.DOTALL)
        return m.group(1).strip() if m else ""

    views    = find("Views")
    likes    = find("Likes")
    comments = find("Comments")
    shares   = find("Shares")

    payouts = re.search(r'Payouts</span>.*?\$([\d.,]+)', html, re.DOTALL)
    payouts = payouts.group(1) if payouts else ""

    # Structure: Approved</span>...<span>82</span>...<span>of <!-- -->314<!-- --> total
    approved_match = re.search(
        r'Approved</span>.*?<span[^>]*>(\d+)</span>.*?of\s*(?:<!--.*?-->)?\s*(\d+)\s*(?:<!--.*?-->)?\s*total',
        html, re.DOTALL
    )
    approved       = approved_match.group(1) if approved_match else ""
    approved_total = approved_match.group(2) if approved_match else ""

    row = {
        "timestamp":      datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
        "views":          parse_number(views)    if views    else "",
        "likes":          parse_number(likes)    if likes    else "",
        "comments":       parse_number(comments) if comments else "",
        "shares":         parse_number(shares)   if shares   else "",
        "payouts":        payouts,
        "approved":       approved,
        "approved_total": approved_total,
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
