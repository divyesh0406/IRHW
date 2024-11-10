import logging
import csv
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)

class Crawler:

    def __init__(self, urls=[], max_rows=20, max_depth = 16,base_domain='nytimes.com', max_threads=5):
        self.visited_urls = set()  # Using a set for faster lookup
        self.urls_to_visit = urls
        self.results = []
        self.max_rows = max_rows
        self.base_domain = base_domain
        self.all_encountered_urls = []  # To store URLs for urls_LATimes.csv
        self.max_threads = max_threads

    def fetch_url_info(self, url):
        try:
            response = requests.get(url, timeout=10)  # Added a timeout for reliability
            content_length = len(response.content)  # Size in bytes
            content_type = response.headers.get('Content-Type', 'unknown')
            return response.text, content_length, content_type, response.status_code
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return None, None, None, None

    def download_url(self, url):
        html, _, _, _ = self.fetch_url_info(url)
        return html

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):  # Relative URL
                path = urljoin(url, path)
            if path:
                links.append(path)
        return links

    def add_url_to_visit(self, url):
        # Only add URLs that belong to latimes.com domain
        if self.check_if_inside_domain(url):
            if url not in self.visited_urls:
                self.visited_urls.add(url)
                return url  # Return URL if it's valid to visit
        return None

    def check_if_inside_domain(self, url):
        parsed_url = urlparse(url)
        # Ensure the URL belongs to latimes.com
        return self.base_domain in parsed_url.netloc

    def crawl(self, url):
        html, content_length, content_type, status_code = self.fetch_url_info(url)
        if html and status_code == 200:
            outlinks = self.get_linked_urls(url, html)
            # Collect data for visit_LATimes.csv
            self.results.append((url, content_length, len(outlinks), content_type))
            # Collect data for urls_LATimes.csv (including repeats)
            for link in outlinks:
                self.all_encountered_urls.append((link, 'OK' if self.check_if_inside_domain(link) else 'N_OK'))
            # Only keep valid outlinks from latimes.com domain
            valid_outlinks = [self.add_url_to_visit(linked_url) for linked_url in outlinks if self.check_if_inside_domain(linked_url)]
            return list(filter(None, valid_outlinks))  # Return valid outlinks for further crawling
        return []

    def run(self):
        # Files for fetch_LATimes.csv, visit_LATimes.csv, and urls_LATimes.csv
        with open('fetch_NYtimes.csv', 'w', newline='', encoding='utf-8') as fetch_file, \
             open('visit_NYtimes.csv', 'w', newline='', encoding='utf-8') as visit_file, \
             open('urls_NYtimes.csv', 'w', newline='', encoding='utf-8') as urls_file:

            # Initialize CSV writers
            fetch_writer = csv.writer(fetch_file)
            visit_writer = csv.writer(visit_file)
            urls_writer = csv.writer(urls_file)

            # Write headers
            fetch_writer.writerow(['URL', 'Status'])
            visit_writer.writerow(['URL', 'Size', 'Number of Outlinks', 'Content_Type'])
            urls_writer.writerow(['URL', 'Type'])

            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                future_to_url = {executor.submit(self.crawl, url): url for url in self.urls_to_visit}

                while future_to_url and len(self.results) < self.max_rows:
                    for future in as_completed(future_to_url):
                        url = future_to_url[future]
                        try:
                            outlinks = future.result()  # Get the outlinks crawled from the URL
                            # Fetch status code and write to fetch_LATimes.csv
                            _, _, _, status_code = self.fetch_url_info(url)
                            if status_code is not None:
                                # Print the URL and status code
                                print(f"Crawled: {url, status_code}")
                                fetch_writer.writerow([url, status_code])

                            # Submit new URLs found (valid outlinks) for crawling
                            for new_url in outlinks:
                                if new_url and new_url not in future_to_url:
                                    future_to_url[executor.submit(self.crawl, new_url)] = new_url

                        except Exception as e:
                            logging.error(f"Error processing {url}: {e}")

            # Write collected data to visit_LATimes.csv
            for result in self.results:
                visit_writer.writerow(result)

            # Write encountered URLs to urls_LATimes.csv
            for url_info in self.all_encountered_urls:
                urls_writer.writerow(url_info)


if __name__ == '__main__':
    Crawler(urls=['https://www.nytimes.com'], max_threads=5).run()
