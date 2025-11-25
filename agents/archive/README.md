# Archived Agents

These agents were used during development and testing but are not part of the final deployment.

## vectorstore_agent.py

**Purpose:** Pure vector similarity search using ChromaDB + Qwen embeddings

**Status:** ⚠️ **Archived** - Low relevance scores (0.19-0.27), poor ranking quality

**Why Archived:**
- Vector embeddings returned very low similarity scores
- Poor ranking quality (1/5 relevant results for "attention mechanism")
- Superseded by `hybrid_rag_agent.py` which combines vector with BM25

**Key Finding:** Vector-only approach was insufficient. The issue was not document imbalance but embeddings/pipeline quality.

---

## bm25_agent.py

**Purpose:** Pure BM25 keyword-based search

**Status:** ✅ **Archived** - Worked perfectly (5/5 for keyword queries)

**Why Archived:**
- Created as diagnostic to test if vector search issue was real
- Proved BM25 keyword matching works perfectly
- Superseded by `hybrid_rag_agent.py` which combines BM25 with vector search for best of both worlds

**Key Finding:** BM25 achieved perfect keyword matching (5/5 relevant chunks), proving the vector search was the problem.

---

## Historical Context

During development, we discovered vector search alone was inadequate:

```
Query: "attention mechanism"

Vector Only: 1/5 relevant (score: 0.27 max) ❌
BM25 Only:   5/5 relevant                   ✅
Hybrid:      5/5 relevant                   ✅
```

The hybrid approach (BM25 + vector) became the recommended solution, combining:
- BM25's perfect keyword matching
- Vector's semantic understanding (when it works)
- BM25 compensates for vector weaknesses

## Final Deployment

The production deployment uses only 2 agents:

1. **filesearch_agent.py** - Terminal-based search (grep/glob/read_file)
2. **hybrid_rag_agent.py** - ⭐ Hybrid RAG (BM25 + vector) - **RECOMMENDED**

## References

- **Implementation Guide:** [../../docs/HYBRID_RAG_IMPLEMENTATION.md](../../docs/HYBRID_RAG_IMPLEMENTATION.md)
- **Test Results:** See `scripts/archive/test_bm25.py` and `test_hybrid_agent.py`
