import os
from tqdm import tqdm
from lib.data_prep import load_and_process_pdfs
from lib.scraper import LawScraper
from dotenv import load_dotenv
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import logging


load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='app.log',
                    filemode='w',
                    encoding='utf-8')

OPEN_AI_KEY = os.getenv("OPENAI_API_KEY")

def split_documents(documents, text_splitter):
    total_docs = len(documents)
    all_splits = []
    
    with tqdm(total=total_docs, desc="Splitting documents") as progress_bar:
        for document in documents:
            splits = text_splitter.split_documents([document])
            all_splits.extend(splits)
            progress_bar.update(1)
    
    return all_splits

def save_cleaned_documents(cleaned_documents, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for doc in cleaned_documents:
            f.write(doc.page_content + "\n")

def batch_process_documents(documents, batch_size, process_function):
    total_docs = len(documents)
    
    with tqdm(total=total_docs, desc="Processing documents in batches") as progress_bar:
        for i in range(0, total_docs, batch_size):
            batch = documents[i:i + batch_size]
            process_function(batch)
            progress_bar.update(len(batch))
            logging.info(f'Processed batch {i//batch_size + 1}/{(total_docs + batch_size - 1)//batch_size}')

def add_documents_to_chromadb(documents):
    vector_db.add_documents(documents)
    logging.info(f'Added {len(documents)} documents to ChromaDB.')

if __name__ == "__main__":
    # scraper = LawScraper('config.json')
    # scraper.get_laws_list()
    # laws_from_json = scraper.load_laws_from_json()
    # scraper.download_pdfs(laws_from_json)

    # pdf_folder_path = "data/pdfs"
    # data = load_and_process_pdfs(pdf_folder_path)
    
    # text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    #     separators=['\n', '\n\n', ',', '.'],
    #     chunk_size=512,
    #     chunk_overlap=64,
    # )

    # splitted_text = split_documents(data, text_splitter)

    vector_db = Chroma(persist_directory="db", embedding_function=OpenAIEmbeddings())

    batch_size = 1000
    # batch_process_documents(splitted_text, batch_size, add_documents_to_chromadb)

    chat_model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)

    prompt_template = """
    You are a knowledgeable tax advisor specialized in German tax laws. Your task is to provide precise and accurate answers to client questions based on given context.
    Be detailed as possible, generate text to be understandable by ordinary people, If you dont know the answer just say you dont know, but do not make up any information that's not from context, and for furture
    guidiance they should contact with RMG Buchhaltung und buroservice. If you don't know an answer, say you don't know and the question. If there is any sensitive and private information
    in the question, refuse to answer the question and alert the client that they cannot share sensitive information.

    Instructions:
    1. Carefully read the client question.
    2. Identify the relevant legal provisions or sections that can answer the question.
    3. Provide a clear and concise answer based on the identified legal text.
    4. Include direct quotes or references from the extracted text to support your answer.
    5. If the question cannot be answered with the available text, provide guidance on where the client might find more information or suggest consulting a tax professional.
    
    {context}
    """

    system_prompt = SystemMessagePromptTemplate(
        prompt=PromptTemplate(
            input_variables=["context"],
            template=prompt_template
        )
    )
    
    human_prompt = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            input_variables=["question"], template="{question}"
        )
    )

    messages = [system_prompt, human_prompt]
    laws_prompt_template = ChatPromptTemplate(
        input_variables=["context", "question"],
        messages=messages,
    )

    relevant_docs = vector_db.as_retriever(k=5)

    chain = (
        {"context": relevant_docs, "question": RunnablePassthrough()}
        | laws_prompt_template
        | chat_model
        | StrOutputParser()
    )

    question = input("Question: ")
    print(chain.invoke(input=question))
