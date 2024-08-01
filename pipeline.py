import csv
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from lib.retrieval import FAISSRetriever
from lib.data_prep import load_and_process_pdfs
from lib.scraper import LawScraper
from lib.indexing import Indexing
from lib.config import config
from evaluation import run_evaluation
import streamlit as st
from langchain_core.messages import BaseMessage
import time
from openai import RateLimitError
from langchain.globals import set_verbose

set_verbose(True)



def stream_data(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.02)


store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
        store[session_id].add_message(BaseMessage(role="assistant", content=laws_list_str))
    return store[session_id]


if __name__ == "__main__":
    ## - RUN FIRST TIME ONLY - comment it out after first run until line 63
    scraper = LawScraper(
        url_base=config['scraper']['url_base'],
        laws_url=config['scraper']['laws_url'],
        json_filepath=config['scraper']['json_filepath'],
        pdf_dir=config['scraper']['pdf_dir']
    )

    scraper.get_laws_list()

    laws_from_json = scraper.load_laws_from_json()

    with open('data/laws_list.csv', mode='w', newline='', encoding='utf-8') as myFile:
        writer = csv.DictWriter(myFile, fieldnames=["Law code", "Law Title", "Link", "pdf_url"])
        writer.writeheader()
        writer.writerows(laws_from_json)

    loader = CSVLoader(file_path='data/laws_list.csv', encoding='latin1')
    laws_list = loader.load()
    laws_list_str = ",\n".join(str(law) for law in laws_list)


    ## - RUN FIRST TIME ONLY - comment it out after first run until line 78
    scraper.download_pdfs(laws_from_json)
    cleaned_documents = load_and_process_pdfs(config['pdf_processing']['pdf_folder_path'])
    documents = cleaned_documents + laws_list

    indexing = Indexing()
    text_splitter = indexing.create_text_splitter()

    splitted_text = indexing.split_documents(documents, text_splitter)
    # #

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    # # - RUN FIRST TIME ONLY - comment it out after first run
    db = FAISS.from_documents(splitted_text, embedding=embeddings)
    db.save_local(folder_path="faiss_vectorstore", index_name="faiss_db")
    # #

    retriever_instance = FAISSRetriever(db_folder_path="faiss_vectorstore")
    retriever = retriever_instance.get_retriever()

    chat_model =ChatOpenAI(model="gpt-4o", temperature=0)

    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        chat_model, retriever, contextualize_q_prompt
    )


    qa_system_prompt = """
    You are a professional lawyer. Answer accurately and precisely based only on the provided context. \
    Always reference the laws and sections exactly as used in your answer. Include the relevant sentence or paragraph. \
    Do not mention anywhere that you have been provided context' \
    If the answer is not in the given context or you don't know it, state that you don't know the answer. \
    Create a scenario to explain the law if necessary. \
    At the end, only for law and legal related question user asked mention the source by naming the laws and the sections. \
    Always print the links in listed format.
    Context: 

    {context} 
    """
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )


    question_answer_chain = create_stuff_documents_chain(chat_model, qa_prompt)

    # # - RUN FIRST TIME ONLY - comment it out to use after first run
    run_evaluation()
    # #

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    st.set_page_config(
        page_title="RAG - Rouhollah Ghobadinezhad",
        initial_sidebar_state="collapsed"
    )

    st.title("Law Chatbot")
    st.write("Ask a question about laws and get precise answers.")
    with st.sidebar:
        with st.container():
            st.header("About")
            st.write("""
                This project is completed in partial fulfillment of the requirements
                for the Bachelor of Computer Science program at SRH Berlin University of Applied Sciences.
                """)
            st.markdown("""
                    **:male-student:**  Rouhollah Ghobadinezhad
                """)
            st.markdown("""
                    **:open_book:**  B.Sc. Computer Science
                """)
            st.markdown("""
                    **:school:**  SRH Berlin University of Applied Sciences
                """)
            st.header("Contact")
            st.write("""
                    If you have any questions or need further assistance, please contact me at:
                """)
            st.markdown("""
                    :email: &nbsp;&nbsp;rouhollahghobadinezhad@gmail.com
                """)
            st.markdown("""
                :arrow_forward: &nbsp;Github: [rougho](https://github.com/rougho)
            """)
            st.markdown("""
                :arrow_forward: &nbsp;LinkedIn: [Rouhollah Ghobadinezhad](https://www.linkedin.com/in/rouhollah-ghobadinezhad-b55b84174)
                """)
            with st.container():
                st.header("Acknowledgement")
                st.write("\n" * 50)
                st.info("This Chatbot can make mistakes, check important informations.", icon="ℹ️")
            


    if "messages" not in st.session_state:
        st.session_state.messages = []


    for message in st.session_state.messages:
        if message["role"] == "user":
            avatar = "😎"
        else:
            avatar = "🦖"
        with st.chat_message(message["role"], avatar=avatar):
            st.write(message["content"])

    if prompt := st.chat_input(placeholder="Your question", max_chars=512):
        # Informational message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="😎"):
            st.write(prompt)        


        try:
            response = rag_chain.invoke({"input": prompt, "chat_history": [{"role": "assistant", "content": laws_list_str}] + st.session_state.messages})
            
            response_content = response["answer"]
            with st.chat_message("assistant", avatar="🦖"):
                with st.spinner("Thinking..."):
                    st.write_stream(stream_data(response_content))
            

            st.session_state.messages.append({"role": "assistant", "content": response_content})
        except RateLimitError:
            with st.chat_message("assistant", avatar="🦖"): 
                st.write("Something went wrong with OpenAI. Please try again later.")
        
        