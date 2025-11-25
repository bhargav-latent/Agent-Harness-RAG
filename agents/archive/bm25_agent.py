"""
BM25 RAG Agent - LangGraph Deployment

This agent uses BM25 keyword-based retrieval instead of broken vector embeddings.
BM25 provides much better retrieval quality for keyword-based queries.
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from deepagents import create_deep_agent
from deepagents.middleware import TodoListMiddleware
from langchain_openai import ChatOpenAI
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import tool

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    base_url=os.getenv("LLM_BASE_URL"),
    model=os.getenv("LLM_MODEL"),
    api_key=os.getenv("OPENAI_API_KEY", "sk-placeholder"),
    temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
    max_tokens=int(os.getenv("LLM_MAX_TOKENS", "8192"))
)

# Load and chunk documents for BM25
documents_dir = os.getenv("DOCUMENTS_DIR", "./rag_data/processed")
loader = DirectoryLoader(
    documents_dir,
    glob="**/*.md",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"}
)
documents = loader.load()

chunk_size = int(os.getenv("CHUNK_SIZE", "512"))
chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "50"))
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap
)
chunks = text_splitter.split_documents(documents)

# Initialize BM25 retriever
bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 10  # Retrieve top 10 by default

# Create BM25 search tools
@tool
def bm25_search(query: str, k: int = 5) -> str:
    """
    Search documents using BM25 keyword matching.

    Args:
        query: The search query
        k: Number of documents to retrieve (default: 5)

    Returns:
        A formatted string containing the retrieved documents
    """
    try:
        # Set k for this query
        original_k = bm25_retriever.k
        bm25_retriever.k = k

        # Perform BM25 search
        results = bm25_retriever.invoke(query)

        # Restore original k
        bm25_retriever.k = original_k

        if not results:
            return "No relevant documents found."

        # Format results
        output = f"Retrieved {len(results)} relevant documents:\\n\\n"

        for i, doc in enumerate(results, 1):
            source = doc.metadata.get('source', 'Unknown')
            # Extract just the filename
            if '\\\\' in source or '/' in source:
                source = Path(source).name

            output += f"--- Document {i} ({source}) ---\\n"
            output += doc.page_content
            output += "\\n\\n"

        return output

    except Exception as e:
        return f"Error performing BM25 search: {str(e)}"

# System prompt for BM25 RAG
system_prompt = """You are a helpful assistant. Always use tools to answer user questions.

You have access to documents through BM25 keyword search (better than broken vector embeddings):
- attention_is_all_you_need.md: Research paper about Transformer architecture
- thinkpython2.md: Python programming book
- The Essence of Software Engineering, Volker Gruhn, Rudiger Striemer.md: Software engineering book

Tool available:
- bm25_search(query, k): Search for relevant documents using keyword matching

When answering questions:
1. Use bm25_search to find relevant information from the documents
2. Base your answer on the retrieved content
3. Cite which document(s) you're referencing

Provide clear, accurate answers with citations."""

# Create Deep Agent with BM25 search and planning middleware
agent = create_deep_agent(
    model=llm,
    system_prompt=system_prompt,
    tools=[bm25_search],
    middleware=[TodoListMiddleware()]
)

# Compile to LangGraph for deployment
graph = agent
