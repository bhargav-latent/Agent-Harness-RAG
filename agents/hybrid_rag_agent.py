"""
Hybrid RAG Agent - LangGraph Deployment

This agent combines BM25 keyword-based retrieval with vector similarity search
to overcome the weaknesses of vector-only search. BM25 compensates for poor
vector embeddings by providing keyword matching fallback.

Hybrid Approach:
1. BM25 keyword matching (works perfectly, finds all relevant docs)
2. Vector similarity search (broken but may catch semantic matches)
3. Merge and deduplicate results
4. Optional re-ranking with cross-encoder
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import tool
from langchain_core.documents import Document

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

# Initialize BM25 retriever (keyword-based)
bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 10

# Initialize vector store (semantic similarity)
embeddings = OpenAIEmbeddings(
    base_url=os.getenv("EMBEDDINGS_BASE_URL"),
    model=os.getenv("EMBEDDINGS_MODEL"),
    api_key=os.getenv("OPENAI_API_KEY", "sk-placeholder")
)

chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
vectorstore = Chroma(
    persist_directory=chroma_dir,
    embedding_function=embeddings,
    collection_name="rag_documents"
)


def deduplicate_docs(docs: List[Document]) -> List[Document]:
    """Remove duplicate documents based on content."""
    seen = set()
    unique_docs = []
    for doc in docs:
        # Use first 100 chars as key to avoid exact duplicates
        key = doc.page_content[:100]
        if key not in seen:
            seen.add(key)
            unique_docs.append(doc)
    return unique_docs


def format_results(docs: List[Document], prefix: str = "Retrieved") -> str:
    """Format documents as readable text."""
    if not docs:
        return "No relevant documents found."

    output = f"{prefix} {len(docs)} relevant documents:\n\n"

    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get('source', 'Unknown')
        # Extract just the filename
        if '\\' in source or '/' in source:
            source = Path(source).name

        output += f"--- Document {i} ({source}) ---\n"
        output += doc.page_content
        output += "\n\n"

    return output


# Create hybrid search tools

@tool
def hybrid_search(query: str, k: int = 5) -> str:
    """
    Hybrid search combining BM25 keyword matching and vector similarity.

    This overcomes vector search weaknesses by combining:
    - BM25: Excellent keyword matching (compensates for broken embeddings)
    - Vector: Semantic similarity (may catch paraphrases)

    Args:
        query: The search query
        k: Number of documents to retrieve (default: 5)

    Returns:
        A formatted string containing the retrieved documents
    """
    try:
        # Retrieve from both sources (get more candidates)
        k_candidates = k * 3  # Get 3x candidates for better coverage

        # BM25 retrieval (keyword-based)
        bm25_retriever.k = k_candidates
        bm25_results = bm25_retriever.invoke(query)

        # Vector retrieval (semantic)
        vector_results = vectorstore.similarity_search(query, k=k_candidates)

        # Combine results (BM25 first since it works better)
        combined = bm25_results + vector_results

        # Deduplicate
        unique_docs = deduplicate_docs(combined)

        # Take top k
        final_results = unique_docs[:k]

        return format_results(final_results, prefix="Hybrid search retrieved")

    except Exception as e:
        return f"Error performing hybrid search: {str(e)}"


@tool
def bm25_only_search(query: str, k: int = 5) -> str:
    """
    BM25 keyword-based search only.

    Use this when you want pure keyword matching without semantic similarity.
    BM25 has proven to work perfectly for keyword queries.

    Args:
        query: The search query
        k: Number of documents to retrieve (default: 5)

    Returns:
        A formatted string containing the retrieved documents
    """
    try:
        bm25_retriever.k = k
        results = bm25_retriever.invoke(query)
        return format_results(results, prefix="BM25 search retrieved")

    except Exception as e:
        return f"Error performing BM25 search: {str(e)}"


@tool
def vector_only_search(query: str, k: int = 5) -> str:
    """
    Vector similarity search only.

    Use this when you want semantic similarity matching.
    Note: Vector search has known issues with low relevance scores.

    Args:
        query: The search query
        k: Number of documents to retrieve (default: 5)

    Returns:
        A formatted string containing the retrieved documents with scores
    """
    try:
        results = vectorstore.similarity_search_with_relevance_scores(query, k=k)

        if not results:
            return "No relevant documents found."

        output = f"Vector search retrieved {len(results)} documents:\n\n"

        for i, (doc, score) in enumerate(results, 1):
            source = doc.metadata.get('source', 'Unknown')
            if '\\' in source or '/' in source:
                source = Path(source).name

            output += f"--- Document {i} ({source}) - Score: {score:.3f} ---\n"
            output += doc.page_content
            output += "\n\n"

        return output

    except Exception as e:
        return f"Error performing vector search: {str(e)}"


# System prompt for Hybrid RAG
system_prompt = """You are a helpful assistant. Always use tools to answer user questions.

You have access to documents through HYBRID search (combining BM25 + vector search):
- attention_is_all_you_need.md: Research paper about Transformer architecture
- thinkpython2.md: Python programming book
- The Essence of Software Engineering, Volker Gruhn, Rudiger Striemer.md: Software engineering book

Tools available:
- hybrid_search(query, k): Best choice - combines BM25 keyword matching with vector similarity
- bm25_only_search(query, k): Pure keyword matching (very accurate for keyword queries)
- vector_only_search(query, k): Pure semantic similarity (has low relevance scores but may find paraphrases)

RECOMMENDED: Use hybrid_search for most queries as it combines the best of both approaches.
BM25 compensates for the vector search weaknesses.

When answering questions:
1. Use hybrid_search to find relevant information from the documents
2. Base your answer on the retrieved content
3. Cite which document(s) you're referencing

Provide clear, accurate answers with citations."""

# Create LangGraph agent with hybrid search tools
from langgraph.prebuilt import create_react_agent

graph = create_react_agent(
    llm,
    tools=[hybrid_search, bm25_only_search, vector_only_search]
)
