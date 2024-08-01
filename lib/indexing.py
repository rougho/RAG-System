import logging
from tqdm import tqdm
from langchain_text_splitters import RecursiveCharacterTextSplitter
from lib.config import config

# Configure logging
logging.basicConfig(level=config['logging']['level'],
                    format=config['logging']['format'],
                    filename=config['logging']['filename'],
                    filemode=config['logging']['filemode'],
                    encoding='utf-8')

class Indexing:
    def __init__(self):
        pass
    
    def create_text_splitter(self, chunk_size=config['pdf_processing']['chunk_size'], chunk_overlap=config['pdf_processing']['chunk_overlap']):
        return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            separators=['\n', '\n\n', ',', '.'],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    
    def split_documents(self, documents, text_splitter):
        total_docs = len(documents)
        all_splits = []
        
        with tqdm(total=total_docs, desc="Splitting documents") as progress_bar:
            for document in documents:
                try:
                    splits = text_splitter.split_documents([document])
                    all_splits.extend(splits)
                    progress_bar.update(1)
                except Exception as e:
                    logging.error(f"Error splitting document: {e}")
        
        return all_splits
