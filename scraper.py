import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib.robotparser
import time
from collections import deque
import logging
import io

# --- CONFIGURATION ---
KB_OUTPUT_DIR = "app/data/kb"  # We will save data inside your app folder
os.makedirs(KB_OUTPUT_DIR, exist_ok=True)

# Setup simple logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1. Hardcoded Q&A (Immediate Answers) ---
# You can add specific answers here that you want the AI to know perfectly.
QA_LIST = [
    {
        "question": "What are the visiting hours?",
        "answer": "Visiting hours are typically from 10:00 AM to 8:00 PM daily. However, specific units like ICU may have restricted timings."
    },
    {
        "question": "Do you accept insurance?",
        "answer": "Yes, Medcare accepts most major insurance providers including Daman, AXA, MetLife, and others. Please contact our front desk for specific policy verification."
    },
    {
        "question": "Where is the hospital located?",
        "answer": "We have multiple branches including Medcare Hospital Al Safa and Medcare Women & Children Hospital. Please specify which branch you are interested in."
    }
]

def ingest_qa():
    """Saves the hardcoded Q&A list."""
    logger.info(f"Ingesting {len(QA_LIST)} Q&A pairs...")
    for i, item in enumerate(QA_LIST):
        data = {
            "title": "FAQ: " + item['question'],
            "url": "internal-faq",
            "content": f"Question: {item['question']}\nAnswer: {item['answer']}",
            "type": "qa"
        }
        filename = os.path.join(KB_OUTPUT_DIR, f"faq_{i+1}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

# --- 2. The Crawler ---
def get_robot_parser(start_url):
    parsed = urlparse(start_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except:
        rp.allow_all = True
    return rp

def scrape_medcare():
    """Scrapes the Medcare website."""
    START_URL = "https://www.medcare.ae/en"
    MAX_PAGES = 50  # Limit to 50 pages for demo speed
    
    logger.info(f"Starting scrape for: {START_URL}")
    
    rp = get_robot_parser(START_URL)
    queue = deque([START_URL])
    visited = set()
    scraped_count = 0
    
    while queue and scraped_count < MAX_PAGES:
        current_url = queue.popleft()
        
        if current_url in visited: continue
        visited.add(current_url)
        
        # Domain Restriction (Stay on medcare.ae)
        if "medcare.ae" not in current_url: continue

        try:
            logger.info(f"Scraping [{scraped_count+1}/{MAX_PAGES}]: {current_url}")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(current_url, headers=headers, timeout=10)
            
            if "text/html" not in response.headers.get('Content-Type', ''):
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # CLEANUP: Remove nav, footer, scripts to get only real text
            for element in soup(["script", "style", "nav", "footer", "header", "noscript", "aside"]):
                element.extract()
            
            # Extract Text
            text = soup.get_text(separator="\n")
            lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 20] # Only keep substantial lines
            cleaned_text = "\n".join(lines)
            
            if len(cleaned_text) > 200:
                page_title = soup.title.string.strip() if soup.title else current_url
                
                data = {
                    "title": page_title,
                    "url": current_url,
                    "content": cleaned_text,
                    "type": "web_page"
                }
                
                # Save as JSON
                safe_name = current_url.replace("https://", "").replace("/", "_").replace(".", "_")[-50:] + ".json"
                with open(os.path.join(KB_OUTPUT_DIR, safe_name), "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                
                scraped_count += 1

            # Find Links
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(current_url, href).split("#")[0]
                if full_url not in visited and "medcare.ae/en" in full_url:
                    queue.append(full_url)
                    
            time.sleep(1) # Be polite

        except Exception as e:
            logger.error(f"Error scraping {current_url}: {e}")

if __name__ == "__main__":
    ingest_qa()
    scrape_medcare()