# import os
# import re
# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.schema import Document

# class PDFCleaner:
#     def __init__(self, file_path):
#         self.file_path = file_path
#         self.loader = PyPDFLoader(file_path)
#         self.pages = self.loader.load_and_split()
    
#     def clean_first_page(self):
#         pattern = r'^(.*?Translations.*?Translations.*?\n)'
#         first_page = self.pages[0]
#         text_content = first_page.page_content
        
#         cleaned_text = re.sub(pattern, '', text_content, count=1, flags=re.DOTALL)
#         first_page.page_content = cleaned_text
#         self.pages[0] = first_page
        
#         return self.pages
    
#     def clean_headers_and_page_numbers(self):
#         header_pattern = (
#             r'Service\s+provided\s+by\s+the\s+Federal\s+Ministry\s+of\s+Justice\s+'
#             r'and\s+the\s+Federal\s+Office\s+of\s+Justice\s+‒\s+www\.gesetze\s*-\s*im\s*-\s*internet\s*\.de'
#         )
#         page_number_pattern = r'Page\s+\d+\s+of\s+\d+'
#         combined_pattern = f'({header_pattern})|({page_number_pattern})'

#         for page in self.pages:
#             page_content = page.page_content
#             cleaned_content = re.sub(combined_pattern, '', page_content, flags=re.IGNORECASE | re.DOTALL)
#             page.page_content = cleaned_content
        
#         return self.pages

# class PDFProcessor:
#     def __init__(self, file_paths):
#         self.file_paths = file_paths
    
#     def process_pdfs(self):
#         cleaned_pages_list = []
#         for file_path in self.file_paths:
#             pdf_cleaner = PDFCleaner(file_path)
#             pdf_cleaner.clean_first_page()
#             cleaned_pages = pdf_cleaner.clean_headers_and_page_numbers()
#             cleaned_pages_list.extend(cleaned_pages)
#         return cleaned_pages_list

# def load_and_process_pdfs(pdf_folder_path):
#     pdf_paths = [os.path.join(pdf_folder_path, file) for file in os.listdir(pdf_folder_path) if file.endswith('.pdf')]
#     pdf_processor = PDFProcessor(pdf_paths)
#     cleaned_documents = pdf_processor.process_pdfs()
#     return cleaned_documents


import os
import re
from langchain_community.document_loaders import PyPDFLoader
from tqdm import tqdm

class PDFCleaner:
    def __init__(self, file_path):
        self.file_path = file_path
        self.loader = PyPDFLoader(file_path)
        self.pages = self.loader.load_and_split()
    
    def clean_first_page(self, progress_bar):
        pattern = r'^(.*?Translations.*?Translations.*?\n)'
        first_page = self.pages[0]
        text_content = first_page.page_content
        
        cleaned_text = re.sub(pattern, '', text_content, count=1, flags=re.DOTALL)
        first_page.page_content = cleaned_text
        self.pages[0] = first_page
        
        progress_bar.update(1)
        return self.pages
    
    def clean_headers_and_page_numbers(self, progress_bar):
        header_pattern = (
            r'Service\s+provided\s+by\s+the\s+Federal\s+Ministry\s+of\s+Justice\s+'
            r'and\s+the\s+Federal\s+Office\s+of\s+Justice\s+‒\s+www\.gesetze\s*-\s*im\s*-\s*internet\s*\.de'
        )
        page_number_pattern = r'Page\s+\d+\s+of\s+\d+'
        combined_pattern = f'({header_pattern})|({page_number_pattern})'

        for page in self.pages:
            page_content = page.page_content
            cleaned_content = re.sub(combined_pattern, '', page_content, flags=re.IGNORECASE | re.DOTALL)
            page.page_content = cleaned_content
            progress_bar.update(1)
        
        return self.pages

class PDFProcessor:
    def __init__(self, file_paths):
        self.file_paths = file_paths
    
    def process_pdfs(self):
        total_steps = sum(len(PyPDFLoader(file_path).load_and_split()) + 1 for file_path in self.file_paths)
        cleaned_pages_list = []
        
        with tqdm(total=total_steps, desc="Process PDFs: ") as progress_bar:
            for file_path in self.file_paths:
                pdf_cleaner = PDFCleaner(file_path)
                pdf_cleaner.clean_first_page(progress_bar)
                cleaned_pages = pdf_cleaner.clean_headers_and_page_numbers(progress_bar)
                cleaned_pages_list.extend(cleaned_pages)
        
        return cleaned_pages_list

def load_and_process_pdfs(pdf_folder_path):
    pdf_paths = [os.path.join(pdf_folder_path, file) for file in os.listdir(pdf_folder_path) if file.endswith('.pdf')]
    pdf_processor = PDFProcessor(pdf_paths)
    cleaned_documents = pdf_processor.process_pdfs()
    return cleaned_documents