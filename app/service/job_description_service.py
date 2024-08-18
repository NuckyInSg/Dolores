from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter

class DocumentService:
    @staticmethod
    def parse_document(file_path: str, is_pdf: bool = False) -> str:
        loader = PyPDFLoader(file_path) if is_pdf else TextLoader(file_path)
        data = loader.load()
        
        text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        docs = text_splitter.split_documents(data)
        
        return " ".join([doc.page_content for doc in docs])

    @classmethod
    def parse_resume(cls, file_path: str) -> str:
        return cls.parse_document(file_path, is_pdf=True)

    @classmethod
    def parse_job_description(cls, file_path: str) -> str:
        return cls.parse_document(file_path, is_pdf=False)