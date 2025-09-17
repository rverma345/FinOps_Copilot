import sqlite3
from pathlib import Path
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


load_dotenv()

# Paths
DB_PATH = Path("data/processed/warehouse.db")  
VECTOR_STORE_PATH = Path("data/processed/vector_store")
DOCS_PATH = Path("docs")  

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment. Set it in .env or docker-compose.")


embeddings_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=OPENAI_API_KEY
)


def ingest_documents(doc_path, vector_path):
    """Load all markdown files and add to Chroma vector store"""
    loader = DirectoryLoader(doc_path, glob="**/*.md", loader_cls=TextLoader)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    vector_db = Chroma.from_documents(chunks, embeddings_model, persist_directory=str(vector_path))
    print(f"Ingested {len(chunks)} markdown document chunks.")


def ingest_synthetic_from_db(db_path, vector_path, table_name):
    """Fetch synthetic dataset rows from SQLite and add to vector store"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch all rows
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    # Get column names
    columns = [desc[0] for desc in cursor.description]
    
    # Convert rows to strings
    texts = [" | ".join(f"{col}: {val}" for col, val in zip(columns, row)) for row in rows]
    conn.close()
    
    # Convert to LangChain Documents
    chunks = [Document(page_content=text) for text in texts]
    
    # Add to vector store
    vector_db = Chroma(persist_directory=str(vector_path), embedding_function=embeddings_model)
    vector_db.add_documents(chunks)
    

    print(f"Ingested {len(chunks)} synthetic rows from table '{table_name}'.")


if __name__ == "__main__":
    VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
    DOCS_PATH.mkdir(exist_ok=True)  # make sure folder exists

    # Ingest markdown docs
    ingest_documents(DOCS_PATH, VECTOR_STORE_PATH)
    
    # Ingest synthetic dataset from SQLite
    ingest_synthetic_from_db(DB_PATH, VECTOR_STORE_PATH, table_name="billing")
    ingest_synthetic_from_db(DB_PATH, VECTOR_STORE_PATH, table_name="resources")


    print("✅ Data ingestion complete (Markdown + Synthetic DB)")
