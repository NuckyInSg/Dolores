from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter

def parse_document(file_path: str, is_pdf: bool = False) -> str:
    loader = PyPDFLoader(file_path) if is_pdf else TextLoader(file_path)
    data = loader.load()
    
    text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    docs = text_splitter.split_documents(data)
    
    return " ".join([doc.page_content for doc in docs])

def parse_resume(file_path: str) -> str:
    return parse_document(file_path, is_pdf=True)

def parse_job_description(file_path: str) -> str:
    return parse_document(file_path, is_pdf=False)