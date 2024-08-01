import os
import json
import nest_asyncio
import openai
import logging
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from ragas.integrations.langchain import EvaluatorChain
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    answer_correctness,
    answer_similarity
)
from tqdm import tqdm
from lib.config import config

logging.basicConfig(level=config['logging']['level'],
                    format=config['logging']['format'],
                    filename=config['logging']['filename'],
                    filemode=config['logging']['filemode'],
                    encoding='utf-8')

class EvaluationPipeline:
    def __init__(self, api_key_env_var='OPENAI_API_KEY', model='gpt-4', temperature=0, max_tokens=None):
        logging.info("Initializing EvaluationPipeline")
        load_dotenv()
        self.api_key = os.environ.get(api_key_env_var)
        openai.api_key = self.api_key
        nest_asyncio.apply()
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.qa_chain = None
        self.metric_chains = {
            'faithfulness': EvaluatorChain(metric=faithfulness),
            'answer_relevancy': EvaluatorChain(metric=answer_relevancy),
            'context_precision': EvaluatorChain(metric=context_precision),
            'context_recall': EvaluatorChain(metric=context_recall),
            'answer_correctness': EvaluatorChain(metric=answer_correctness),
            'answer_similarity': EvaluatorChain(metric=answer_similarity)
        }
        self.result = []
        logging.info("EvaluationPipeline initialized successfully")

    def set_retriever(self, retriever):
        logging.info("Setting retriever")
        self.qa_chain = RetrievalQA.from_chain_type(
            self.llm,
            retriever=retriever,
            return_source_documents=True
        )
        logging.info("Retriever set successfully")

    def load_dataset(self, filepath):
        logging.info(f"Loading dataset from {filepath}")
        try:
            with open(filepath, "r", encoding='utf-8') as file:
                dataset = json.load(file)
            logging.info("Dataset loaded successfully")
            return dataset
        except Exception as e:
            logging.error(f"Failed to load dataset: {e}")
            raise

    def evaluate(self, eval_dataset):
        logging.info("Starting evaluation of the dataset")
        for data in tqdm(eval_dataset, desc="Evaluating dataset"):
            inputs = []
            for q, a, c, gt in zip(data["question"], data["answer"], data["contexts"], data["ground_truth"]):
                inputs.append({
                    "question": q,
                    "answer": a,
                    "contexts": c,
                    "ground_truth": gt
                })

            for input_data in inputs:
                result_template = {
                    'question': input_data['question'],
                    'answer': input_data['answer'],
                    'context': input_data['contexts'],
                    'ground_truth': input_data['ground_truth']
                }
                for metric_name, chain in self.metric_chains.items():
                    result_template[metric_name] = chain.invoke(input_data)[metric_name]
                self.result.append(result_template)
        logging.info("Evaluation completed successfully")

    def save_results(self, filepath):
        logging.info(f"Saving results to {filepath}")
        try:
            with open(filepath, "w", encoding='utf-8') as file:
                json.dump(self.result, file, indent=4)
            logging.info("Results saved successfully")
        except Exception as e:
            logging.error(f"Failed to save results: {e}")
            raise