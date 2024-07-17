import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from lib.data_prep import load_and_process_pdfs
from lib.scraper import LawScraper
from lib.indexing import Indexing
from lib.retrieval import Retrieval
from lib.prompting import Prompting
from lib.chat_history import ChatHistoryManager
from lib.config import config

load_dotenv()

logging.basicConfig(level=config['logging']['level'],
                    format=config['logging']['format'],
                    filename=config['logging']['filename'],
                    filemode=config['logging']['filemode'],
                    encoding='utf-8')

if __name__ == "__main__":
    try:
        scraper = LawScraper(
            url_base=config['scraper']['url_base'],
            laws_url=config['scraper']['laws_url'],
            json_filepath=config['scraper']['json_filepath'],
            pdf_dir=config['scraper']['pdf_dir']
        )
        scraper.get_laws_list()
        laws_from_json = scraper.load_laws_from_json()
        scraper.download_pdfs(laws_from_json)

        cleaned_documents = load_and_process_pdfs(config['pdf_processing']['pdf_folder_path'])

        indexing = Indexing()
        text_splitter = indexing.create_text_splitter()

        splitted_text = indexing.split_documents(cleaned_documents, text_splitter)

        indexing.batch_process_documents(splitted_text, process_function=indexing.add_documents_to_chromadb)

        chat_model = ChatOpenAI(model=config['openai']['model'], temperature=config['openai']['temperature'])

        retrieval = Retrieval()
        history_aware_retriever = retrieval.create_history_aware_retriever(chat_model)

        prompting = Prompting()
        qa_prompt = prompting.create_qa_prompt()
        question_answer_chain = prompting.create_question_answer_chain(chat_model, qa_prompt)
        rag_chain = prompting.create_rag_chain(history_aware_retriever, question_answer_chain)

        chat_history_manager = ChatHistoryManager()

        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            chat_history_manager.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

        session_id = config['application']['session_id']

        while True:
            user_input = input("User: ")
            if user_input.lower() in config['application']['exit_commands']:
                print("Exiting conversation.")
                break
            
            response = conversational_rag_chain.invoke(
                {"input": user_input},
                config={
                    "configurable": {"session_id": session_id}
                }
            )["answer"]
            
            print(f"Assistant: {response}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
