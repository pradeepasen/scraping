import time
import csv
import requests
from bs4 import BeautifulSoup
from urllib import robotparser

HN_URL = "https://news.ycombinator.com/"
ROBOTS_URL = "https://news.ycombinator.com/robots.txt"
HEADERS = {"User-Agent": "SafeEducationalScraper/1.0"}
CSV_FILE = "data.csv"

rp = robotparser.RobotFileParser()
rp.set_url(ROBOTS_URL)
rp.read()

if not rp.can_fetch(HEADERS["User-Agent"], HN_URL):
    print("Scraping the front page is NOT allowed by robots.txt. Exiting.")
    exit()

crawl_delay = rp.crawl_delay(HEADERS["User-Agent"])
if crawl_delay is None:
    crawl_delay = 30

print(f"Respecting crawl delay: {crawl_delay} seconds…")
time.sleep(crawl_delay)

response = requests.get(HN_URL, headers=HEADERS)
soup = BeautifulSoup(response.text, "html.parser")

stories = []

for rank, item in enumerate(soup.select(".athing"), start=1):
    title_tag = item.select_one(".titleline > a")
    if not title_tag:
        continue

    title = title_tag.text.strip()
    link = title_tag.get("href")

    subtext = item.find_next_sibling("tr").select_one(".subtext")
    score_tag = subtext.select_one(".score") if subtext else None
    score = score_tag.text if score_tag else "0 points"

    stories.append([rank, title, link, score])

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Rank", "Title", "URL", "Score"])
    writer.writerows(stories)

print(f"\nCSV created successfully → {CSV_FILE}")
print(f"Total stories saved: {len(stories)}")

print("\n=== FIRST 5 STORIES (Preview) ===\n")
print(f"{'Rank':<5} | {'Title':<60} | {'Score':<12}")
print("-" * 90)

for row in stories[:5]:
    rank, title, link, score = row
    short_title = (title[:57] + "...") if len(title) > 60 else title
    print(f"{rank:<5} | {short_title:<60} | {score:<12}")

print("\nPreview complete. All stories stored safely in hn_stories.csv.")
