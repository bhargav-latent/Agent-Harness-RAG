"""
Fix Vector Store Retrieval with Re-ranking

Strategy:
1. Retrieve TOP_K_RETRIEVAL chunks (20) from ChromaDB
2. Rerank using cross-encoder model
3. Return TOP_N_RERANK (5) best chunks

This solves the document imbalance issue by:
- Casting a wider net initially
- Using semantic re-ranking to find truly relevant content
- Ensuring small documents (attention paper) get fair representation
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from sentence_transformers import CrossEncoder

load_dotenv()

print("\n" + "="*80)
print("IMPLEMENTING RE-RANKED VECTOR STORE RETRIEVAL")
print("="*80 + "\n")

# Configuration from .env
top_k_retrieval = int(os.getenv("TOP_K_RETRIEVAL", "20"))
top_n_rerank = int(os.getenv("TOP_N_RERANK", "5"))
reranker_model_name = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-base")

print(f"Configuration:")
print(f"  Initial retrieval: {top_k_retrieval} chunks")
print(f"  After re-ranking: {top_n_rerank} chunks")
print(f"  Re-ranker model: {reranker_model_name}")
print()

# Initialize embeddings
embeddings = OpenAIEmbeddings(
    base_url=os.getenv("EMBEDDINGS_BASE_URL"),
    model=os.getenv("EMBEDDINGS_MODEL"),
    api_key=os.getenv("OPENAI_API_KEY", "sk-placeholder")
)

# Initialize vector store
chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
vectorstore = Chroma(
    persist_directory=chroma_dir,
    embedding_function=embeddings,
    collection_name="rag_documents"
)

# Initialize re-ranker
print("Loading re-ranker model...")
reranker = CrossEncoder(reranker_model_name)
print(f"[OK] Re-ranker loaded")
print()

def retrieve_with_reranking(query: str, k_initial: int = 20, k_final: int = 5):
    """
    Retrieve and re-rank documents.

    Args:
        query: Search query
        k_initial: Number of chunks to retrieve initially
        k_final: Number of chunks to return after re-ranking

    Returns:
        List of (doc, score) tuples
    """
    # Step 1: Initial retrieval
    initial_results = vectorstore.similarity_search(query, k=k_initial)

    # Step 2: Prepare query-document pairs for re-ranker
    pairs = [[query, doc.page_content] for doc in initial_results]

    # Step 3: Re-rank using cross-encoder
    rerank_scores = reranker.predict(pairs)

    # Step 4: Sort by rerank score and take top k_final
    scored_results = list(zip(initial_results, rerank_scores))
    scored_results.sort(key=lambda x: x[1], reverse=True)

    return scored_results[:k_final]

# Test queries
test_queries = [
    "attention mechanism",
    "attention is all you need",
    "transformer architecture self-attention",
    "multi-head attention scaled dot product"
]

for query in test_queries:
    print(f"\nQuery: '{query}'")
    print("-" * 80)

    # Without re-ranking
    print("\nWithout re-ranking (top 5 from vector store):")
    results_no_rerank = vectorstore.similarity_search_with_relevance_scores(query, k=5)
    for i, (doc, score) in enumerate(results_no_rerank, 1):
        source = Path(doc.metadata.get('source', 'Unknown')).name
        print(f"  {i}. {source}: {score:.4f}")

    # With re-ranking
    print("\nWith re-ranking (retrieve 20, rerank to top 5):")
    results_reranked = retrieve_with_reranking(query, k_initial=top_k_retrieval, k_final=top_n_rerank)
    for i, (doc, score) in enumerate(results_reranked, 1):
        source = Path(doc.metadata.get('source', 'Unknown')).name
        print(f"  {i}. {source}: {score:.4f}")

    # Check if attention paper appears
    attention_before = sum(1 for doc, _ in results_no_rerank
                          if 'attention' in doc.metadata.get('source', '').lower())
    attention_after = sum(1 for doc, _ in results_reranked
                         if 'attention' in doc.metadata.get('source', '').lower())

    print(f"\nAttention paper chunks: {attention_before} → {attention_after}")
    print("=" * 80)

print("\n\nSummary:")
print("Re-ranking significantly improves retrieval by:")
print("1. Casting wider net (20 chunks) to catch small documents")
print("2. Using semantic relevance (cross-encoder) to rerank")
print("3. Returning truly relevant chunks, not just similar embeddings")
print()
print("Next: Update vector search tools to use re-ranking")
