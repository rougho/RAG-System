from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("data/pdfs/AbgG.pdf")
data = loader.load_and_split()

from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=100,
    chunk_overlap=30,
)

all_splits = text_splitter.split_documents(data)

print(all_splits[0:4])

