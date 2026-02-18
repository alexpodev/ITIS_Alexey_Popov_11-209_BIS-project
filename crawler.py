import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs, urlencode

BASE_URL = "https://media.kpfu.ru"
NEWS_URL = "https://media.kpfu.ru/news"
OUTPUT_DIR = "crawl_output"
INDEX_FILE = "index.txt" 
MIN_PAGES = 100
REQUEST_DELAY = 0.5 

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}


def is_text_page(html_content):
    if not html_content:
        return False
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    for tag in soup(['script', 'style', 'meta', 'link']):
        tag.decompose()

    text = soup.get_text(strip=True)
    
    if len(text) < 100:
        return False
    
    cyrillic_pattern = re.compile(r'[\u0400-\u04FF]')
    if not cyrillic_pattern.search(text):
        latin_pattern = re.compile(r'[a-zA-Z]{3,}')
        if not latin_pattern.search(text):
            return False
    
    return True


def extract_article_links(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    links = set()
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        
        if href.startswith('#') or href.startswith('javascript:'):
            continue
        
        full_url = urljoin(BASE_URL, href)
        
        if urlparse(full_url).netloc != urlparse(BASE_URL).netloc:
            continue
        
        parsed = urlparse(full_url)
        path = parsed.path.lower()
        
        if any(path.endswith(ext) for ext in ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.pdf', '.doc', '.docx']):
            continue
        
        if 'rss' in path.lower():
            continue
        
        query_params = parse_qs(parsed.query)
        if path == '/news' or path == '/news/':
            continue
        
        if '/news' in path:
            links.add(full_url)
    
    return links


def fetch_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def save_page(content, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath


def crawl():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    visited_urls = set()
    article_urls = set()
    saved_pages = []
    page_counter = 0
    
    print(f"Target: {NEWS_URL}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Minimum pages to download: {MIN_PAGES}")
    print("-" * 50)
        
    print(f"Fetching main news page: {NEWS_URL}")
    html = fetch_page(NEWS_URL)
    if html:
        new_links = extract_article_links(html)
        article_urls.update(new_links)
        print(f"Found {len(new_links)} article URLs")
  
    max_pages_to_try = 30
    for page_num in range(1, max_pages_to_try + 1):
        paginated_url = f"{NEWS_URL}?page={page_num}"
        print(f"Fetching page {page_num}: {paginated_url}")
        
        html = fetch_page(paginated_url)
        if not html:
            print(f"Failed to fetch, stopping pagination")
            break
        
        soup = BeautifulSoup(html, 'html.parser')
        news_items = soup.find_all('a', href=True)
        new_links = extract_article_links(html)
        
        if not new_links:
            print(f"No more articles found, stopping pagination")
            break
        
        article_urls.update(new_links)
        print(f"Found {len(new_links)} new article URLs (total: {len(article_urls)})")
        
        time.sleep(REQUEST_DELAY)
    
    print(f"\nCollected {len(article_urls)} unique article URLs")
        
    index_entries = []
    
    for url in article_urls:
        if len(saved_pages) >= MIN_PAGES:
            break
        
        print(f"Downloading ({len(saved_pages) + 1}/{MIN_PAGES}): {url}")
        
        html = fetch_page(url)
        if not html:
            continue
        
        if not is_text_page(html):
            print(f"Skipped: Not a text page")
            continue
        
        page_counter += 1
        filename = f"page_{page_counter:04d}.txt" 
        save_page(html, filename)
        saved_pages.append((page_counter, url, filename))
        index_entries.append(f"{page_counter}\t{url}")
        
        print(f"Saved: {filename}")
        
        time.sleep(REQUEST_DELAY)
    
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(script_dir, INDEX_FILE)
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("# File Number\tURL\n")
        f.write("#" + "=" * 60 + "\n")
        for entry in index_entries:
            f.write(entry + "\n")
    
    print(f"  Index file created: {index_path}")
    
    print(f"Pages downloaded: {len(saved_pages)}")
    print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}")
    print(f"Index file: {os.path.abspath(index_path)}")
    
    return len(saved_pages)


if __name__ == "__main__":
    crawl()
