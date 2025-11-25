"""
Query Vector Store Directly

Test script to query the ChromaDB vector store and display results with similarity scores.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Load environment variables
load_dotenv()

def query_vectorstore(query: str, k: int = 5):
    """Query the vector store and display results with similarity scores."""

    # Initialize embeddings
    embeddings = OpenAIEmbeddings(
        base_url=os.getenv("EMBEDDINGS_BASE_URL"),
        model=os.getenv("EMBEDDINGS_MODEL"),
        api_key=os.getenv("OPENAI_API_KEY", "sk-placeholder")
    )

    # Load vector store
    chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    vectorstore = Chroma(
        persist_directory=chroma_dir,
        embedding_function=embeddings,
        collection_name="rag_documents"
    )

    print(f"\nQuerying vector store: '{query}'")
    print(f"Retrieving top {k} results with similarity scores...\n")
    print("=" * 120)

    # Perform similarity search with scores
    results = vectorstore.similarity_search_with_relevance_scores(query, k=k)

    if not results:
        print("No relevant documents found.")
        return

    # Display results in table format
    print(f"\n{'Rank':<6} {'Source':<50} {'Score':<8} {'Preview':<50}")
    print("-" * 120)

    for i, (doc, score) in enumerate(results, 1):
        source = doc.metadata.get('source', 'Unknown')
        # Extract just the filename
        if '\\' in source or '/' in source:
            source = Path(source).name

        # Get preview of content (first 100 chars)
        preview = doc.page_content[:100].replace('\n', ' ').strip()
        # Handle special characters for Windows console
        preview = preview.encode('ascii', errors='replace').decode('ascii')
        if len(doc.page_content) > 100:
            preview += "..."

        print(f"{i:<6} {source:<50} {score:<8.4f} {preview:<50}")

    print("=" * 120)

    # Display full content of top result
    print(f"\n\nFull content of top result (Score: {results[0][1]:.4f}):")
    print("-" * 120)
    print(f"Source: {Path(results[0][0].metadata.get('source', 'Unknown')).name}")
    print("-" * 120)
    print(results[0][0].page_content)
    print("-" * 120)

if __name__ == "__main__":
    query_vectorstore("attention mechanism", k=10)
