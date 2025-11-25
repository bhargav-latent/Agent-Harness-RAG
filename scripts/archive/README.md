# Archived Scripts

This folder contains diagnostic and test scripts used during development and troubleshooting. These scripts are preserved for reference but are not part of the core functionality.

## Diagnostic Scripts

### check_chroma_config.py
**Purpose:** Verify ChromaDB configuration and collection status
**Status:** Archived - used during vector store debugging

### diagnose_embeddings.py
**Purpose:** Comprehensive embeddings diagnostics (dimensions, normalization, similarity tests)
**Status:** Archived - confirmed embeddings technically correct but retrieval scores low

### query_vectorstore.py
**Purpose:** Direct vector store query testing with similarity scores
**Status:** Archived - used to identify low relevance score issue (0.19-0.27)

## Experimental Scripts

### fix_vectorstore_retrieval.py
**Purpose:** Attempted fix using re-ranking with cross-encoder
**Status:** Archived - re-ranking approach not implemented in final agents

### test_hybrid_retrieval.py
**Purpose:** Document-aware retrieval strategy experiment
**Status:** Archived - simpler hybrid approach (BM25 + vector) implemented instead

## Test Scripts

### test_bm25.py
**Purpose:** Compare BM25 vs vector search side-by-side
**Result:** Proved BM25 perfect (5/5) while vector search broken (1/5)
**Status:** Archived - results documented in HYBRID_RAG_IMPLEMENTATION.md

### test_hybrid_agent.py
**Purpose:** Test hybrid retrieval (BM25 + vector) quality
**Result:** Confirmed hybrid achieves 5/5 perfect results
**Status:** Archived - results validated, hybrid agent deployed

## Key Findings

These scripts led to critical discoveries:
1. Vector embeddings return very low similarity scores (0.19-0.27)
2. BM25 keyword matching works perfectly (5/5 for "attention mechanism")
3. Hybrid approach (BM25 + vector) combines best of both worlds
4. Document imbalance was NOT the issue - embeddings/pipeline quality was the problem

## References

- [HYBRID_RAG_IMPLEMENTATION.md](../../HYBRID_RAG_IMPLEMENTATION.md) - Full implementation guide
- [agents/hybrid_rag_agent.py](../../agents/hybrid_rag_agent.py) - Production hybrid agent
- [agents/bm25_agent.py](../../agents/bm25_agent.py) - BM25-only agent
