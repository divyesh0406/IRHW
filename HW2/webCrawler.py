import logging
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import mimetypes

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)

lock = threading.Lock()

class Crawler:

    def __init__(self, urls=[], max_rows=20000, domain='usatoday.com'):
        self.visited_urls = set()
        self.urls_to_visit = urls
        self.discovered_urls = set() 
        self.max_rows = max_rows
        self.result_file_fetch = 'fetch_USAToday2.csv'
        self.result_file_visit = 'visit_USAToday2.csv'
        self.result_file_urls = 'urls_USAToday2.csv'
        self.num_fetched = 0
        self.domain = domain

        with open(self.result_file_fetch, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['URL', 'Status'])  

        with open(self.result_file_visit, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['URL', 'Size (Bytes)', 'No. of Outlinks', 'Content-Type']) 

        with open(self.result_file_urls, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['URL', 'Location'])  

    def download_url(self, url):
        try:
            response = requests.get(url, timeout=10)
            content_length = len(response.content) 
            content_type = response.headers.get('Content-Type', '')
            if content_type.startswith('text/html'):
                content_type = 'text/html'  
            return response.status_code, response.text, content_length, content_type
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return None, None, None, None

    def get_linked_urls(self, base_url, html):
        soup = BeautifulSoup(html, 'html.parser')
        outlinks = 0
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(base_url, path)
            if path and path.startswith('http'):  
                yield path
                outlinks += 1
        return outlinks

    def add_url_to_visit(self, url):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)

    def check_url_location(self, url):
        parsed_url = urlparse(url)
        if self.domain in parsed_url.netloc:
            return 'OK'  
        return 'N_OK'  

    def filter_url(self, url):
        allowed_extensions = ['.html', '.htm', '.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif']
        parsed_url = urlparse(url)
        file_extension = mimetypes.guess_extension(parsed_url.path.split('?')[0]) or ''  # Ignore query params
        is_internal = self.domain in parsed_url.netloc
        return (parsed_url.path.endswith('/') or file_extension in allowed_extensions) and is_internal

    def save_fetch_result(self, url, status):
        with lock:
            if self.num_fetched >= self.max_rows:
                return
            with open(self.result_file_fetch, 'a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([url, status])
            self.num_fetched += 1

    def save_visit_result(self, url, content_length, outlinks, content_type):
        with lock:
            with open(self.result_file_visit, 'a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([url, content_length, outlinks, content_type])

    def save_discovered_url(self, url, location):
        with lock:
            if url not in self.discovered_urls: 
                self.discovered_urls.add(url)
                with open(self.result_file_urls, 'a', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow([url, location])

    def crawl(self, url):
        if self.num_fetched >= self.max_rows:
            return

        logging.info(f'Crawling: {url}')
        status, html, content_length, content_type = self.download_url(url)
        if status is None:
            return

        self.save_fetch_result(url, status)

        if html:
            linked_urls = list(self.get_linked_urls(url, html))
            outlinks = len(linked_urls)  # Count of outlinks
            self.save_visit_result(url, content_length, outlinks, content_type)

            for linked_url in linked_urls:
                if self.filter_url(linked_url):
                    location = self.check_url_location(linked_url)
                    self.save_discovered_url(linked_url, location)
                    self.add_url_to_visit(linked_url)

    def run(self):
        with ThreadPoolExecutor(max_workers=10) as executor:  
            futures = {}
            while self.urls_to_visit and self.num_fetched < self.max_rows:
                if len(futures) < 10 and self.urls_to_visit:
                    url = self.urls_to_visit.pop(0)
                    if url not in self.visited_urls:
                        self.visited_urls.add(url)
                        futures[executor.submit(self.crawl, url)] = url

                for future in as_completed(futures.keys()):
                    try:
                        future.result()
                    except Exception as e:
                        logging.error(f'Error during crawling: {e}')
                    finally:
                        futures.pop(future)  

if __name__ == '__main__':
    seed_urls = ['https://www.usatoday.com']
    crawler = Crawler(urls=seed_urls, max_rows=20000, domain='usatoday.com')
    crawler.run()
