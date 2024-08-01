import os
import re
import logging
from langchain_community.document_loaders import PyPDFLoader
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from lib.config import config

# Configure logging
logging.basicConfig(level=config['logging']['level'],
                    format=config['logging']['format'],
                    filename=config['logging']['filename'],
                    filemode=config['logging']['filemode'],
                    encoding='utf-8')

class PDFCleaner:
    def __init__(self, file_path):
        self.file_path = file_path
        self.loader = PyPDFLoader(file_path)
        self.pages = self.loader.load_and_split()
        logging.info(f"Loaded and split PDF: {file_path}")
    
    def clean_first_page(self, progress_bar):
        pattern = r'^(.*?Translations.*?Translations.*?\n)'
        first_page = self.pages[0]
        text_content = first_page.page_content
        
        cleaned_text = re.sub(pattern, '', text_content, count=1, flags=re.DOTALL)
        first_page.page_content = cleaned_text
        self.pages[0] = first_page
        
        progress_bar.update(1)
        logging.info(f"Cleaned first page of PDF: {self.file_path}")

        return self.pages
    
    def clean_headers_and_page_numbers(self, progress_bar):
        logging.info(f"Started cleaning headers and page numbers for PDF: {self.file_path}")
        
        # Define patterns for header and page number
        header_pattern = r"Service provided by the Federal Ministry of Justice\s+and the Federal Office of Justice ‒ www\.gesetze\s+-im-internet\.de\s+"

        page_number_pattern = re.compile(r'Page\s+\d+\s+of\s+\d+', re.IGNORECASE | re.DOTALL)
        
        # Process each page to remove headers and page numbers
        for page in self.pages:
            page_content = page.page_content
            
            # Clean the headers and page numbers from the content
            cleaned_content = re.sub(header_pattern,'', page_content)
            cleaned_content = page_number_pattern.sub('', cleaned_content)
            page.page_content = cleaned_content
            
            progress_bar.update(1)
        
        logging.info(f"Finished cleaning headers and page numbers for PDF: {self.file_path}")
        return self.pages


class PDFProcessor:
    def __init__(self, file_paths):
        self.file_paths = file_paths
    
    def process_pdfs(self):
        logging.info("Started processing PDFs")
        total_steps = sum(len(PyPDFLoader(file_path).load_and_split()) + 1 for file_path in self.file_paths)
        cleaned_pages_list = []
        
        with tqdm(total=total_steps, desc="Process PDFs: ") as progress_bar:
            with ThreadPoolExecutor(max_workers=4) as executor:
                results = list(executor.map(self._process_single_pdf, [(file_path, progress_bar) for file_path in self.file_paths]))
                for cleaned_pages in results:
                    cleaned_pages_list.extend(cleaned_pages)
        
        logging.info("Finished processing all PDFs")
        return cleaned_pages_list
    
    def _process_single_pdf(self, args):
        file_path, progress_bar = args
        pdf_cleaner = PDFCleaner(file_path)
        pdf_cleaner.clean_first_page(progress_bar)
        return pdf_cleaner.clean_headers_and_page_numbers(progress_bar)

def load_and_process_pdfs(pdf_folder_path=config['pdf_processing']['pdf_folder_path']):
    logging.info(f"Loading and processing PDFs from folder: {pdf_folder_path}")
    pdf_paths = [os.path.join(pdf_folder_path, file) for file in os.listdir(pdf_folder_path) if file.endswith('.pdf')]
    pdf_processor = PDFProcessor(pdf_paths)
    cleaned_documents = pdf_processor.process_pdfs()
    logging.info(f"Finished loading and processing PDFs from folder: {pdf_folder_path}")
    return cleaned_documents

# if __name__ == "__main__":
#     load_and_process_pdfs()
# import os
# import re
# import logging
# from langchain_community.document_loaders import PyPDFLoader
# from tqdm import tqdm
# from concurrent.futures import ThreadPoolExecutor
# from .config import config

# # Configure logging
# logging.basicConfig(level=config['logging']['level'],
#                     format=config['logging']['format'],
#                     filename=config['logging']['filename'],
#                     filemode=config['logging']['filemode'],
#                     encoding='utf-8')

# class PDFCleaner:
#     def __init__(self, file_path):
#         self.file_path = file_path
#         self.loader = PyPDFLoader(file_path)
#         self.pages = self.loader.load()
#         logging.info(f"Loaded and split PDF: {file_path}")
    
#     def clean_first_page(self, progress_bar):
#         pattern = r'^(.*?Translations.*?Translations.*?\n)'
#         first_page = self.pages[0]
#         text_content = first_page.page_content
        
#         logging.debug(f"Original first page content: {text_content[:500]}")  # Debug log
        
#         cleaned_text = re.sub(pattern, '', text_content, count=1, flags=re.DOTALL)
#         first_page.page_content = cleaned_text
#         self.pages[0] = first_page
        
#         progress_bar.update(1)
#         logging.info(f"Cleaned first page of PDF: {self.file_path}")

#         return self.pages
    
#     def clean_headers_and_page_numbers(self, progress_bar):
#         logging.info(f"Started cleaning headers and page numbers for PDF: {self.file_path}")
        
#         # Define patterns for header and page number
#         header_pattern = r"Service provided by the Federal Ministry of Justice\s+and the Federal Office of Justice ‒ www\.gesetze\s+-im-internet\.de\s+"

#         page_number_pattern = re.compile(r'Page\s+\d+\s+of\s+\d+', re.IGNORECASE | re.DOTALL)
        
#         for page in self.pages:
#             page_content = page.page_content
#             logging.debug(f"Original content: {page_content[:500]}")  # Debug log
#             cleaned_content = re.sub(header_pattern,'', page_content)
#             cleaned_content = page_number_pattern.sub('', cleaned_content)
#             logging.debug(f"Cleaned content: {cleaned_content[:500]}")  # Debug log
#             page.page_content = cleaned_content
            
#             progress_bar.update(1)
        
#         logging.info(f"Finished cleaning headers and page numbers for PDF: {self.file_path}")
#         return self.pages


# class PDFProcessor:
#     def __init__(self, file_paths):
#         self.file_paths = file_paths
    
#     def process_pdfs(self):
#         logging.info("Started processing PDFs")
#         total_steps = sum(len(PyPDFLoader(file_path).load_and_split()) + 1 for file_path in self.file_paths)
#         cleaned_pages_list = []
        
#         with tqdm(total=total_steps, desc="Process PDFs: ") as progress_bar:
#             with ThreadPoolExecutor(max_workers=4) as executor:
#                 results = list(executor.map(self._process_single_pdf, [(file_path, progress_bar) for file_path in self.file_paths]))
#                 for cleaned_pages in results:
#                     cleaned_pages_list.extend(cleaned_pages)
        
#         logging.info("Finished processing all PDFs")
#         return cleaned_pages_list
    
#     def _process_single_pdf(self, args):
#         file_path, progress_bar = args
#         pdf_cleaner = PDFCleaner(file_path)
#         pdf_cleaner.clean_first_page(progress_bar)
#         return pdf_cleaner.clean_headers_and_page_numbers(progress_bar)

# def load_and_process_pdfs(pdf_folder_path=config['pdf_processing']['pdf_folder_path']):
#     logging.info(f"Loading and processing PDFs from folder: {pdf_folder_path}")
#     pdf_paths = [os.path.join(pdf_folder_path, file) for file in os.listdir(pdf_folder_path) if file.endswith('.pdf')]
#     pdf_processor = PDFProcessor(pdf_paths)
#     cleaned_documents = pdf_processor.process_pdfs()
#     logging.info(f"Finished loading and processing PDFs from folder: {pdf_folder_path}")
#     return cleaned_documents
