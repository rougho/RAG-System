from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from lib.config import config

class Retrieval:
    def __init__(self, persist_directory=config['database']['persist_directory']):
        self.vector_db = Chroma(persist_directory=persist_directory, embedding_function=OpenAIEmbeddings())

    def get_relevant_docs(self):
        return self.vector_db.as_retriever(k=5)

    def create_history_aware_retriever(self, chat_model):
        contextualize_q_system_prompt = (
            "You are a knowledgeable tax advisor specialized in German tax laws. "
            "Given a chat history and the latest user question which might reference context in the chat history, "
            "reformulate the user question into a standalone question that can be understood without the chat history. "
            "Ensure the reformulated question retains all relevant details for accurate advice on German tax laws. "
            "Do NOT answer the question, just reformulate it if needed and otherwise return it as is. "
            "Be specific and include any necessary context about tax regulations, compliance, or related advice."
        )

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        relevant_docs = self.get_relevant_docs()
        
        return create_history_aware_retriever(chat_model, relevant_docs, contextualize_q_prompt)
