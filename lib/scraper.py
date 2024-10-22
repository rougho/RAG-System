import os
import requests
from bs4 import BeautifulSoup as bs
import json
import re
from tqdm import tqdm
import logging
import validators
import time
from lib.config import config

# Configure logging
logging.basicConfig(level=config['logging']['level'],
                    format=config['logging']['format'],
                    filename=config['logging']['filename'],
                    filemode=config['logging']['filemode'],
                    encoding='utf-8')


def validate_url(url):
    if validators.url(url):
        logging.info(f"Validated URL: {url}")
        return True
    else:
        logging.error(f"Invalid URL: {url}")
        raise ValueError(f"Invalid URL: {url}")

def validate_path(path):
    if os.path.exists(path):
        logging.info(f"Validated path: {path}")
        return True
    else:
        logging.error(f"Invalid Path: {path}")
        raise ValueError(f"Invalid Path: {path}")


class LawScraper:
    def __init__(self, url_base, laws_url, json_filepath, pdf_dir):
        self.url_base = url_base
        self.laws_url = laws_url
        self.json_filepath = json_filepath
        self.pdf_dir = pdf_dir

        validate_url(self.url_base)
        validate_url(self.laws_url)
        os.makedirs(os.path.dirname(self.json_filepath), exist_ok=True)
        os.makedirs(self.pdf_dir, exist_ok=True)
        
    def fetch_laws_page(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            logging.info(f"Fetched laws page successfully from {url}")
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching laws page from {url}: {e}")
            raise

    def parse_laws(self, html_content):
        soup = bs(html_content, 'html.parser')
        laws = []

        empty_title_count = 0

        for p in soup.find_all('p'):
            a_tag = p.find('a')
            if a_tag and a_tag.get('href') and a_tag.text:
                act_code = a_tag.text.strip()
                link = a_tag.get('href')
                law_title = p.find('abbr')['title'] if p.find('abbr') else ''

                if law_title == '' and empty_title_count < 2:
                    empty_title_count += 1
                    continue

                pdf_url = link.split('/')[0]
                pdf_url = f"{self.url_base}{pdf_url}/{pdf_url}.pdf"
                laws.append({'Law code': act_code, 'Law Title': law_title, 'Link': f"{self.url_base}{link}", 'pdf_url': pdf_url})
        
        logging.info(f"Parsed {len(laws)} laws from HTML content")
        return laws

    def save_laws_to_json(self, laws):
        try:
            with open(self.json_filepath, 'w', encoding='utf-8') as f:
                json.dump(laws, f, ensure_ascii=False, indent=4)
            logging.info(f"Laws saved to {self.json_filepath}")
        except Exception as e:
            logging.error(f"Error saving laws to JSON: {e}")
            raise

    def print_laws(self, laws):
        for law in tqdm(laws, desc="Getting laws list: "):
            data = f"Law Code: {law['Law code']}\nLaw Title: {law['Law Title']}\nLink: {law['Link']}\nPDF: {law['pdf_url']}"
            logging.info(data)
            print(data)

    def get_laws_list(self):
        html_content = self.fetch_laws_page(self.laws_url)
        laws = self.parse_laws(html_content)
        self.save_laws_to_json(laws)
        print("Laws have been saved to", self.json_filepath)
        # self.print_laws(laws)

    def load_laws_from_json(self):
        try:
            with open(self.json_filepath, 'r', encoding='utf-8') as f:
                laws = json.load(f)
            logging.info(f"Laws loaded from {self.json_filepath}")
            return laws
        except Exception as e:
            logging.error(f"Error loading laws from JSON: {e}")
            raise

    @staticmethod
    def sanitize_filename(filename):
        sanitized = re.sub(r'[\\/*?:"<>|]', "_", filename)
        logging.info(f"Sanitized filename: {sanitized}")
        return sanitized

    def delete_existing_pdfs(self):
        try:
            if os.path.exists(self.pdf_dir):
                pdf_files = [f for f in os.listdir(self.pdf_dir) if f.endswith('.pdf')]
                for pdf_file in tqdm(pdf_files, desc="Deleting old PDFs"):
                    os.remove(os.path.join(self.pdf_dir, pdf_file))
            logging.info(f"Existing PDFs deleted from {self.pdf_dir}")
        except Exception as e:
            logging.error(f"Error deleting existing PDFs: {e}")
            raise

    def download_pdfs(self, laws):
        self.delete_existing_pdfs()
        os.makedirs(self.pdf_dir, exist_ok=True)
        for law in tqdm(laws, desc="Downloading PDFs"):
            pdf_url = law['pdf_url']
            pdf_title = self.sanitize_filename(law['Law code'])
            pdf_path = os.path.join(self.pdf_dir, f"{pdf_title}.pdf")
            try:
                self.download_with_retries(pdf_url, pdf_path, pdf_title)
            except Exception as e:
                logging.error(f"Failed to download {pdf_title}: {e}")
                tqdm.write(f"Failed to download {pdf_title}: {e}")

    def download_with_retries(self, url, path, title, retries=3, delay=5):
        for attempt in range(retries):
            try:
                response = requests.get(url)
                response.raise_for_status()
                with open(path, 'wb') as pdf_file:
                    pdf_file.write(response.content)
                logging.info(f"Downloaded: {title}")
                tqdm.write(f"Downloaded: {title}")
                return
            except requests.exceptions.RequestException as e:
                logging.error(f"Attempt {attempt + 1} failed for {title}: {e}")
                time.sleep(delay)
        raise Exception(f"Failed to download {title} after {retries} attempts")
