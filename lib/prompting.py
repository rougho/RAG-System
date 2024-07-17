from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import MessagesPlaceholder

class Prompting:
    def create_qa_prompt(self):
        system_prompt = (
            "You are a knowledgeable tax advisor specialized in German tax laws."
            "Your task is to provide precise and accurate answers to client questions."
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Be detailed as possible, generate text to be understandable by ordinary people, "
            "If you dont know the answer just say you dont know, but do not make up any information that's not from context."
            "If there is any sensitive and private information in the question, refuse to answer the question and alert the client that they cannot share sensitive information."
            "If the question is unclear or have lack of keywords, ask the client to be more specific."
            "For further guidance they should contact RMG Buchhaltung und buroservice."
            "'RMG Buchhaltung un buroservice' website is 'www.rmg-buchhaltung.de' "
            "and phone number '+49 176 6638 1041' and email address 'kontakt@rmg-buchhaltung.de'."
            "\n\n"
            "{context}"
        )

        return ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

    def create_question_answer_chain(self, chat_model, qa_prompt):
        return create_stuff_documents_chain(chat_model, qa_prompt)

    def create_rag_chain(self, history_aware_retriever, question_answer_chain):
        return create_retrieval_chain(history_aware_retriever, question_answer_chain)
