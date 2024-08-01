from lib.evaluator import EvaluationPipeline
from lib.retrieval import FAISSRetriever
from lib.visualizer import MetricsPlotter
import json
from tqdm import tqdm
import random


def load_result(file_path):
    with open(file_path, "r", encoding='utf-8') as file:
        result = json.load(file)
    return result


def metrics_extractor(eval_result):
    metrics = []
    print("Extracting metrics...")
    for data in tqdm(eval_result, desc="Processing results"):
        temp = {
            'faithfulness': data['faithfulness'],
            'answer_relevancy': data['answer_relevancy'],
            'context_precision': data['context_precision'],
            'context_recall': data['context_recall'],
            'answer_correctness': data['answer_correctness'],
            'answer_similarity': data['answer_similarity']
        }
        metrics.append(temp)
    return metrics


def get_single_question(evaluation_results):
    random.seed()
    index = int(random.randint(0, 9))
    return evaluation_results[int(index)]


def plotter(metrics, title, output_filepath):
    plotter = MetricsPlotter(
        metrics,
        title=title,
        output_file=output_filepath
    )
    print("Plotting metrics...")
    plotter.plot_metrics()
    print(f"Plot saved to {output_filepath}\n\n")


def run_evaluation():
    retriever_instance = FAISSRetriever(db_folder_path="faiss_vectorstore")
    retriever = retriever_instance.get_retriever()

    eval_pipeline = EvaluationPipeline()
    eval_pipeline.set_retriever(retriever)

    eval_dataset = eval_pipeline.load_dataset("data/evaluation/eval_dataset.json")

    eval_pipeline.evaluate(eval_dataset)

    eval_pipeline.save_results("data/evaluation/result.json")

    evaluation_results = load_result("data/evaluation/result.json")

    total_metrics = metrics_extractor(evaluation_results)
    plotter(metrics=total_metrics,
            title='Retrieval Augmented Generation Pipeline - Evaluation',
            output_filepath='data/evaluation/evaluation_plot.html')

    single_question_metrics = [get_single_question(evaluation_results)]

    single_metrics = metrics_extractor(single_question_metrics)
    plotter(metrics=single_metrics,
            title=single_question_metrics[0]['question'],
            output_filepath='data/evaluation/single_question_evaluation_plot.html')


if __name__ == "__main__":
    run_evaluation()