"""
Vector Store RAG Agent - LangGraph Deployment

This agent uses Deep Agents framework with a custom vector similarity search tool
to retrieve and answer questions from a ChromaDB vector store.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from deepagents import create_deep_agent
from deepagents.middleware import TodoListMiddleware
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
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

# Initialize embeddings
embeddings = OpenAIEmbeddings(
    base_url=os.getenv("EMBEDDINGS_BASE_URL"),
    model=os.getenv("EMBEDDINGS_MODEL"),
    api_key=os.getenv("OPENAI_API_KEY", "sk-placeholder")
)

# Initialize ChromaDB vector store
chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
vectorstore = Chroma(
    persist_directory=chroma_dir,
    embedding_function=embeddings,
    collection_name="rag_documents"
)

# Create vector search tool
@tool
def vector_search(query: str, k: int = 5) -> str:
    """
    Search the vector store for documents relevant to the query.

    Args:
        query: The search query
        k: Number of documents to retrieve (default: 5)

    Returns:
        A formatted string containing the retrieved documents with metadata
    """
    try:
        # Perform similarity search
        results = vectorstore.similarity_search(query, k=k)

        if not results:
            return "No relevant documents found."

        # Format results
        output = f"Retrieved {len(results)} relevant documents:\n\n"

        for i, doc in enumerate(results, 1):
            source = doc.metadata.get('source', 'Unknown')
            # Extract just the filename
            if '\\' in source or '/' in source:
                source = source.split('\\')[-1].split('/')[-1]

            output += f"--- Document {i} ({source}) ---\n"
            output += doc.page_content
            output += "\n\n"

        return output

    except Exception as e:
        return f"Error performing vector search: {str(e)}"

@tool
def vector_search_with_scores(query: str, k: int = 5) -> str:
    """
    Search the vector store and return documents with similarity scores.

    Args:
        query: The search query
        k: Number of documents to retrieve (default: 5)

    Returns:
        A formatted string containing retrieved documents with similarity scores
    """
    try:
        # Perform similarity search with scores
        results = vectorstore.similarity_search_with_relevance_scores(query, k=k)

        if not results:
            return "No relevant documents found."

        # Format results
        output = f"Retrieved {len(results)} relevant documents with scores:\n\n"

        for i, (doc, score) in enumerate(results, 1):
            source = doc.metadata.get('source', 'Unknown')
            # Extract just the filename
            if '\\' in source or '/' in source:
                source = source.split('\\')[-1].split('/')[-1]

            output += f"--- Document {i} ({source}) - Relevance: {score:.3f} ---\n"
            output += doc.page_content
            output += "\n\n"

        return output

    except Exception as e:
        return f"Error performing vector search with scores: {str(e)}"

# System prompt for Vector Store RAG
system_prompt = """You are a helpful assistant. Always use tools to answer user questions.

You have access to documents through semantic vector search:
- attention_is_all_you_need.md: Research paper about Transformer architecture
- thinkpython2.md: Python programming book
- The Essence of Software Engineering, Volker Gruhn, Rudiger Striemer.md: Software engineering book

Tools available:
- vector_search(query, k): Search for relevant documents using semantic similarity
- vector_search_with_scores(query, k): Same as vector_search but includes relevance scores

When answering questions:
1. Use vector_search to find relevant information from the documents
2. Base your answer on the retrieved content
3. Cite which document(s) you're referencing

Provide clear, accurate answers with citations."""

# Create Deep Agent with vector search tools and planning middleware
# Note: No backend parameter needed - Deep Agents will use default backend for LangGraph
agent = create_deep_agent(
    model=llm,
    system_prompt=system_prompt,
    tools=[vector_search, vector_search_with_scores],
    middleware=[TodoListMiddleware()]
)

# Compile to LangGraph for deployment
graph = agent
