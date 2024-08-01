import logging
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from lib.config import config

logging.basicConfig(level=config['logging']['level'],
                    format=config['logging']['format'],
                    filename=config['logging']['filename'],
                    filemode=config['logging']['filemode'],
                    encoding='utf-8')

class FAISSRetriever:
    def __init__(self, db_folder_path, embeddings_model="text-embedding-3-large", index_name="faiss_db"):
        logging.info("Initializing FAISSRetriever")
        self.db_folder_path = db_folder_path
        self.embeddings_model = embeddings_model
        self.index_name = index_name
        self.retriever = None
        self.load_retriever()
        logging.info("FAISSRetriever initialized successfully")

    def load_retriever(self):
        logging.info(f"Loading retriever with model: {self.embeddings_model}, index: {self.index_name}")
        try:
            embeddings = OpenAIEmbeddings(model=self.embeddings_model)
            db = FAISS.load_local(folder_path=self.db_folder_path, embeddings=embeddings, index_name=self.index_name, allow_dangerous_deserialization=True)
            self.retriever = db.as_retriever(search_type="mmr", search_kwargs={"k": 10})
            logging.info("Retriever loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load retriever: {e}")
            raise

    def get_retriever(self):
        if self.retriever:
            logging.info("Retriever is ready to be returned")
            return self.retriever
        else:
            error_msg = "Retriever has not been initialized"
            logging.error(error_msg)
            raise ValueError(error_msg)