import logging
from tqdm import tqdm
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from lib.config import config

# Configure logging
logging.basicConfig(level=config['logging']['level'],
                    format=config['logging']['format'],
                    filename=config['logging']['filename'],
                    filemode=config['logging']['filemode'],
                    encoding='utf-8')

class Indexing:
    def __init__(self, persist_directory=config['database']['persist_directory']):
        self.vector_db = Chroma(persist_directory=persist_directory, embedding_function=OpenAIEmbeddings())
    
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

    def save_cleaned_documents(self, cleaned_documents, output_file):
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for doc in cleaned_documents:
                    f.write(doc.page_content + "\n")
        except Exception as e:
            logging.error(f"Error saving cleaned documents: {e}")

    def add_documents_to_chromadb(self, documents):
        try:
            self.vector_db.add_documents(documents)
            logging.info(f'Added {len(documents)} documents to ChromaDB.')
        except Exception as e:
            logging.error(f"Error adding documents to ChromaDB: {e}")

    def batch_process_documents(self, documents, batch_size=config['pdf_processing']['batch_size'], process_function=None):
        total_docs = len(documents)
        
        with tqdm(total=total_docs, desc="Processing documents in batches") as progress_bar:
            for i in range(0, total_docs, batch_size):
                batch = documents[i:i + batch_size]
                try:
                    if process_function:
                        process_function(batch)
                    progress_bar.update(len(batch))
                    logging.info(f'Processed batch {i//batch_size + 1}/{(total_docs + batch_size - 1)//batch_size}')
                except Exception as e:
                    logging.error(f"Error processing batch: {e}")
