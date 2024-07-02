from lib.scraper import LawScraper
from lib.data_prep import load_and_process_pdfs
from langchain_text_splitters import RecursiveCharacterTextSplitter

from tqdm import tqdm





def split_documents(documents, text_splitter):
    total_docs = len(documents)
    all_splits = []
    
    with tqdm(total=total_docs, desc="Splitting documents") as progress_bar:
        for document in documents:
            splits = text_splitter.split_documents([document])
            all_splits.extend(splits)
            progress_bar.update(1)
    
    return all_splits


if __name__ == "__main__":

    scraper = LawScraper('config.json')
    scraper.get_laws_list()

    laws_from_json = scraper.load_laws_from_json()
    scraper.download_pdfs(laws_from_json)

    # pdf_folder_path = "data/pdfs"
    # data = load_and_process_pdfs(pdf_folder_path)
    
    # text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    #     chunk_size=512,
    #     chunk_overlap=30,
    # )

    # all_splits = split_documents(data, text_splitter)

    # with open("splitted.txt", "w", encoding="utf-8") as f:
    #     for split in all_splits:
    #         print(split.pages[5])
    #         f.write(split + "\n")