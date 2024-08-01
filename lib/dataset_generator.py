# from ragas.testset.generator import TestsetGenerator
# from ragas.testset.evolutions import simple, reasoning, multi_context
# from langchain_openai import ChatOpenAI
# dataset = documents[4800:5000]

# # generator with openai models
# generator_llm = ChatOpenAI(model="gpt-4o-mini")
# critic_llm = ChatOpenAI(model="gpt-4")
# embeddings = embeddings

# generator = TestsetGenerator.from_langchain(
#     generator_llm,
#     critic_llm,
#     embeddings
# )

# # generate testset
# testset = generator.generate_with_langchain_docs(dataset, test_size=3, distributions={simple: 0.5, reasoning: 0.25, multi_context: 0.25})

# testset.to_pandas().to_json("data3.json", indent=4)


# questions_list = [
#     "What content is banned in Germany in WhatsApp profile pictures?",
#     "What is the significance of a land charge in relation to the permanent residential right?",
#     "What initiatives does the Federal Bar Association promote to support the professional development of lawyers?",
#     "What rights are aggrieved persons notified of in criminal proceedings?",
#     "What is the value of electronic hand-written signature?",
#     "What factors about employee consent and data processing should be weighed for legal compliance and balancing employer-employee interests?",
#     "What are the conditions under which the processing of special categories of personal data is permitted?",
#     "What is the process required for the consolidation of mining proprietorship fields?",
#     "What's the Central Register's role in special e-legal mailboxes?",
#     "How do the Federal Admin Court's rulings relate to the supervisory authority?"
# ]

# responses = {
#     "question": [],
#     "answer": [],
#     "contexts": [],
#     "ground_truth": []
# }

# dataset = []

#rag pipeline to generater answer to datasets questions

# response = rag_chain.invoke({"input": q, "chat_history": chat_history})
# for question in questions_list:
#     chat_history = [laws_string]
    
#     responses = {
#     "question": [],
#     "answer": [],
#     "contexts": [],
#     "ground_truth": []
#     }
#     response = rag_chain.invoke({"input": question, "chat_history": chat_history})
#     responses["question"].append(question)
#     responses["answer"].append(response["answer"])
#     responses["contexts"].append([f"Document {index + 1}: {content.page_content}" for index, content in enumerate(response['context'])])
#     dataset.append(responses)

# with open("data/evaluation/eval_dataset.json", "w", encoding='utf-8') as final:
#   json.dump(dataset, final, indent=4)