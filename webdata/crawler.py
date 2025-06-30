import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from collections import deque
import time
import random

class SimpleCrawler:
    def __init__(self, seed_url, max_pages=50):
        self.seed = seed_url
        self.domain = urlparse(seed_url).netloc
        self.max_pages = max_pages
        self.visited = set()
        self.queue = deque([seed_url])

    def crawl(self):
        while self.queue and len(self.visited) < self.max_pages:
            url = self.queue.popleft()
            if url in self.visited:
                continue

            try:
                resp = requests.get(url, timeout=5)
                resp.raise_for_status()
            except requests.RequestException as e:
                print(f"Failed to fetch {url}: {e}")
                continue

            self.visited.add(url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else 'No title'
            print(f"[{len(self.visited)}] {title} — {url}")
            time.sleep(random.uniform(0.5, 2.0))


            for link_tag in soup.find_all('a', href=True):
                link = urljoin(url, link_tag['href'])
                parsed = urlparse(link)
                # keep only http[s], same domain, no fragments
                if parsed.scheme in ('http', 'https') and parsed.netloc == self.domain:
                    clean = parsed._replace(fragment='').geturl()
                    if clean not in self.visited:
                        self.queue.append(clean)

if __name__ == '__main__':
    start = 'https://valedosinconfidentes.com.br/'
    crawler = SimpleCrawler(start, max_pages=1000)
    crawler.crawl()
