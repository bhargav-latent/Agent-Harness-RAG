"""
Initialize Vector Store with Document Embeddings

This script:
1. Loads markdown documents from rag_data/processed
2. Splits documents into chunks
3. Generates embeddings using configured endpoint
4. Stores in ChromaDB for vector similarity search
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

def initialize_vectorstore():
    """Initialize ChromaDB vector store with document embeddings."""

    print("\n" + "="*80)
    print("INITIALIZING VECTOR STORE")
    print("="*80 + "\n")

    # Configuration
    documents_dir = os.getenv("DOCUMENTS_DIR", "./rag_data/processed")
    chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    chunk_size = int(os.getenv("CHUNK_SIZE", "512"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "50"))

    print(f"Documents directory: {documents_dir}")
    print(f"ChromaDB directory: {chroma_dir}")
    print(f"Chunk size: {chunk_size}")
    print(f"Chunk overlap: {chunk_overlap}\n")

    # 1. Load documents
    print("Step 1: Loading markdown documents...")
    loader = DirectoryLoader(
        documents_dir,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    print(f"[OK] Loaded {len(documents)} documents")

    # Print document info
    for doc in documents:
        filename = Path(doc.metadata['source']).name
        print(f"  - {filename}: {len(doc.page_content)} characters")

    # 2. Split documents into chunks
    print("\nStep 2: Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"[OK] Created {len(chunks)} chunks")

    # Print chunking stats
    chunk_lengths = [len(chunk.page_content) for chunk in chunks]
    print(f"  - Average chunk size: {sum(chunk_lengths) / len(chunk_lengths):.0f} characters")
    print(f"  - Min chunk size: {min(chunk_lengths)} characters")
    print(f"  - Max chunk size: {max(chunk_lengths)} characters")

    # 3. Initialize embeddings
    print("\nStep 3: Initializing embedding model...")
    embeddings = OpenAIEmbeddings(
        base_url=os.getenv("EMBEDDINGS_BASE_URL"),
        model=os.getenv("EMBEDDINGS_MODEL"),
        api_key=os.getenv("OPENAI_API_KEY", "sk-placeholder")
    )
    print(f"[OK] Using embeddings endpoint: {os.getenv('EMBEDDINGS_BASE_URL')}")
    print(f"  Model: {os.getenv('EMBEDDINGS_MODEL')}")

    # 4. Create vector store
    print("\nStep 4: Creating ChromaDB vector store...")
    print("[...] Generating embeddings and storing vectors (this may take a while)...")

    # Remove existing vector store if it exists
    if os.path.exists(chroma_dir):
        print(f"  Removing existing vector store at {chroma_dir}")
        import shutil
        shutil.rmtree(chroma_dir)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=chroma_dir,
        collection_name="rag_documents"
    )

    print(f"[OK] Vector store created with {len(chunks)} embeddings")
    print(f"  Persisted to: {chroma_dir}")

    # 5. Test retrieval
    print("\nStep 5: Testing vector store retrieval...")
    test_query = "What is the attention mechanism?"
    results = vectorstore.similarity_search(test_query, k=3)
    print(f"[OK] Test query: '{test_query}'")
    print(f"  Retrieved {len(results)} documents:")
    for i, doc in enumerate(results, 1):
        source = Path(doc.metadata['source']).name
        preview = doc.page_content[:100].replace('\n', ' ')
        print(f"  {i}. {source}: {preview}...")

    print("\n" + "="*80)
    print("[SUCCESS] VECTOR STORE INITIALIZED SUCCESSFULLY")
    print("="*80 + "\n")

    return vectorstore

if __name__ == "__main__":
    try:
        vectorstore = initialize_vectorstore()
        print("Vector store is ready for use!")
    except Exception as e:
        print(f"\n[ERROR] Error initializing vector store: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
