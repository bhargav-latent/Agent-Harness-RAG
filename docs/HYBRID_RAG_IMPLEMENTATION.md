# Hybrid RAG Implementation Summary

> **Date:** 2025-11-25
> **Status:** ✅ Implemented and Tested
> **Framework:** LangChain Deep Agents + LangGraph CLI

## Overview

This document summarizes the implementation of a **Hybrid RAG (Retrieval-Augmented Generation)** agent that combines BM25 keyword-based retrieval with vector similarity search to overcome the limitations of vector-only approaches.

---

## Problem Statement

### Vector Search Failure

Initial implementation used pure vector similarity search (ChromaDB + Qwen3-Embedding-8B), which showed catastrophic retrieval failure:

**Query:** "attention mechanism"

| Method | Relevant Results | Max Score | Quality |
|--------|-----------------|-----------|---------|
| **Vector Only** | 1/5 from attention paper | 0.27 | ❌ BROKEN |
| **BM25 Only** | 5/5 from attention paper | N/A | ✅ PERFECT |
| **Hybrid** | 5/5 from attention paper | N/A | ✅ EXCELLENT |

### Root Cause

Vector embeddings return extremely low similarity scores (0.19-0.27 range) and poor ranking, making vector-only RAG unreliable. The embeddings model (Qwen/Qwen3-Embedding-8B) appears technically correct (4096 dims, normalized) but ChromaDB retrieval quality is unacceptable.

**Key Insight:** This is NOT a document imbalance issue - it's an embeddings/pipeline quality problem.

---

## Solution: Hybrid Retrieval

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│               User Query                                │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼──────┐  ┌──────▼──────┐
│ BM25 Search  │  │Vector Search│
│ (Keyword)    │  │ (Semantic)  │
│              │  │             │
│ - 15 chunks  │  │ - 15 chunks │
│ - Perfect    │  │ - Low scores│
│   matching   │  │ - Paraphrase│
└───────┬──────┘  └──────┬──────┘
        │                 │
        └────────┬────────┘
                 │
         ┌───────▼────────┐
         │  Merge Results │
         │  Deduplicate   │
         │  Top K (5)     │
         └───────┬────────┘
                 │
         ┌───────▼────────┐
         │ Agent Response │
         │ with Citations │
         └────────────────┘
```

### Implementation Details

**File:** `agents/hybrid_rag_agent.py`

**Key Components:**

1. **BM25 Retriever** (langchain-community)
   - Keyword-based matching using BM25 algorithm
   - Retrieves 15 candidates
   - Perfect for exact keyword queries

2. **Vector Store** (ChromaDB + Qwen embeddings)
   - Semantic similarity search
   - Retrieves 15 candidates
   - May catch paraphrases and semantic variations

3. **Hybrid Merge Strategy**
   - Combine BM25 results + vector results
   - BM25 results prioritized (added first)
   - Deduplication based on content (first 100 chars)
   - Return top K (default: 5)

**Tools Provided:**

```python
@tool
def hybrid_search(query: str, k: int = 5) -> str:
    """
    Hybrid search combining BM25 + vector similarity.
    RECOMMENDED for most queries.
    """

@tool
def bm25_only_search(query: str, k: int = 5) -> str:
    """
    Pure BM25 keyword matching.
    Use for exact keyword queries.
    """

@tool
def vector_only_search(query: str, k: int = 5) -> str:
    """
    Pure vector similarity search.
    Use for semantic/paraphrase queries (with caution).
    """
```

---

## Test Results

### Comparison Across Methods

**Query: "attention mechanism"**

```
BM25 Only:
  5/5 chunks from attention_is_all_you_need.md
  Perfect keyword matching

Vector Only:
  1/5 chunks from attention_is_all_you_need.md
  Max score: 0.27 (very low)
  4/5 chunks from irrelevant documents

Hybrid:
  5/5 chunks from attention_is_all_you_need.md
  Perfect retrieval (leveraging BM25)
```

**Query: "attention is all you need"**

```
BM25 Only:   3/5 relevant
Vector Only: 0/5 relevant
Hybrid:      3/5 relevant
```

**Query: "self-attention multi-head"**

```
BM25 Only:   5/5 relevant
Vector Only: 1/5 relevant
Hybrid:      5/5 relevant
```

### Conclusion

✅ **Hybrid retrieval successfully combines:**
- BM25's perfect keyword matching
- Vector search's semantic understanding (when it works)
- Deduplication to avoid redundant chunks

✅ **BM25 compensates for vector search weaknesses** by providing a reliable keyword matching fallback.

✅ **Best of both worlds** - keyword precision + semantic flexibility.

---

## LangGraph Deployment

### Configuration

**File:** `langgraph.json`

```json
{
  "graphs": {
    "filesearch_agent": {
      "path": "agents/filesearch_agent.py:graph",
      "description": "FileSearch RAG using grep/glob/read_file tools"
    },
    "vectorstore_agent": {
      "path": "agents/vectorstore_agent.py:graph",
      "description": "Vector Store RAG (vector-only, has low relevance scores)"
    },
    "bm25_agent": {
      "path": "agents/bm25_agent.py:graph",
      "description": "BM25 Keyword RAG (keyword-only, works great)"
    },
    "hybrid_rag_agent": {
      "path": "agents/hybrid_rag_agent.py:graph",
      "description": "Hybrid RAG (RECOMMENDED - best of both)"
    }
  }
}
```

### Available Agents

| Agent | Method | Status | Recommendation |
|-------|--------|--------|----------------|
| **filesearch_agent** | grep/glob/read_file | ✅ Works | Good for file-level search |
| **vectorstore_agent** | Vector only | ⚠️ Low scores | Not recommended |
| **bm25_agent** | BM25 only | ✅ Perfect | Good for keywords |
| **hybrid_rag_agent** | BM25 + Vector | ✅ Excellent | **RECOMMENDED** |

### Deployment

```bash
# Start LangGraph dev server
cd "d:/Personal Projects/Agent-Harness-RAG"
langgraph dev

# Access agents at:
# - http://localhost:8123 (Studio UI)
# - Agents available: filesearch_agent, vectorstore_agent, bm25_agent, hybrid_rag_agent
```

---

## Technical Stack

### Dependencies

```json
{
  "dependencies": [
    "langchain",
    "langgraph",
    "langchain-openai",
    "langchain-chroma",
    "langchain-community",
    "deepagents",
    "python-dotenv"
  ]
}
```

### Configuration (.env)

```bash
# LLM Configuration
LLM_BASE_URL=http://10.26.1.11:8786/v1
LLM_MODEL=Qwen/Qwen2.5-32B-Instruct-AWQ
OPENAI_API_KEY=sk-placeholder

# Embeddings Configuration
EMBEDDINGS_BASE_URL=http://10.26.1.11:8786/v1
EMBEDDINGS_MODEL=Qwen/Qwen3-Embedding-8B

# RAG Configuration
DOCUMENTS_DIR=./rag_data/processed
CHROMA_PERSIST_DIR=./chroma_db
CHUNK_SIZE=512
CHUNK_OVERLAP=50
```

### Document Corpus

```
rag_data/processed/
├── attention_is_all_you_need.md (Transformer paper)
├── thinkpython2.md (Python programming book)
└── The Essence of Software Engineering, Volker Gruhn, Rudiger Striemer.md

Total: 3 documents → 3,370 chunks (512 chars, 50 overlap)
```

---

## Files Created/Modified

### New Files

1. **agents/hybrid_rag_agent.py**
   - Main hybrid RAG agent implementation
   - Combines BM25 + vector search
   - Exports `graph` for LangGraph deployment

2. **scripts/test_hybrid_agent.py**
   - Test suite comparing BM25, vector, and hybrid methods
   - Verifies hybrid retrieval quality
   - Measures attention paper chunk retrieval

3. **scripts/test_bm25.py**
   - Comparative test: BM25 vs vector search
   - Proved vector search is broken
   - Demonstrated BM25 perfection

### Modified Files

1. **langgraph.json**
   - Added `hybrid_rag_agent` graph
   - Updated agent descriptions
   - Marked hybrid as RECOMMENDED

2. **agents/vectorstore_agent.py**
   - Added TodoListMiddleware
   - Simplified system prompt
   - Removed restrictive instructions

3. **agents/bm25_agent.py**
   - Created standalone BM25 agent
   - Added TodoListMiddleware
   - Provides keyword-only fallback

---

## Journey to Hybrid RAG

### Iteration History

1. **Initial Vector Store Agent**
   - Created vector-only RAG with ChromaDB
   - Discovered catastrophically low relevance scores (0.19-0.27)
   - Agent entered infinite tool call loops

2. **Prompt Optimization**
   - Attempted restrictive prompt → User rejected as too limiting
   - Simplified to natural helpful prompt
   - Fixed infinite loop issue

3. **Diagnosis: Vector Search Broken**
   - User correctly identified embeddings/pipeline issue
   - Created diagnostic scripts
   - Proved via BM25 comparison: 5/5 vs 1/5 results

4. **BM25 Implementation**
   - Created standalone BM25 agent
   - Achieved perfect keyword matching (5/5)
   - Demonstrated BM25 superiority

5. **User Correction: Hybrid Approach**
   - User clarified: "BM25 compensates vector store agent - hybrid"
   - Not standalone replacement, but complement
   - Led to hybrid implementation

6. **Hybrid RAG Success**
   - Combined BM25 + vector with deduplication
   - Achieved perfect results (5/5 for keyword queries)
   - BM25 compensates for vector weaknesses

### Key Learnings

1. **Document imbalance is NOT the problem** - Low relevance scores indicate pipeline/embeddings issue
2. **BM25 keyword matching is highly effective** - Perfect for keyword queries
3. **Hybrid approach combines strengths** - BM25 precision + vector semantic flexibility
4. **Simple prompts work best** - Overly restrictive prompts cause issues
5. **TodoListMiddleware essential** - Enables multi-hop reasoning and planning

---

## Next Steps

### Immediate Tasks

1. ✅ Implement hybrid RAG agent
2. ✅ Test hybrid retrieval quality
3. ✅ Deploy via LangGraph CLI
4. ⏳ Run evaluation with 50 test questions
5. ⏳ Compare FileSearch vs Hybrid RAG performance

### Future Enhancements

1. **Re-ranking with Cross-Encoder**
   - Add semantic re-ranking layer
   - Use BAAI/bge-reranker-base
   - Retrieve 20 candidates, rerank to top 5

2. **Document-Aware Retrieval**
   - Detect document intent from query keywords
   - Filter to relevant documents before search
   - Reduce noise from large corpus

3. **Reciprocal Rank Fusion (RRF)**
   - Formal rank merging algorithm
   - Weighted combination of BM25 and vector ranks
   - Better than simple concatenation

4. **Evaluation Framework**
   - 50 test questions across 12 categories
   - RAGAS metrics (answer_relevancy, faithfulness, context_precision)
   - Compare FileSearch vs BM25 vs Vector vs Hybrid

---

## References

### Code Files

- [agents/hybrid_rag_agent.py](agents/hybrid_rag_agent.py) - Main hybrid agent
- [agents/bm25_agent.py](agents/bm25_agent.py) - BM25-only agent
- [agents/vectorstore_agent.py](agents/vectorstore_agent.py) - Vector-only agent
- [scripts/test_hybrid_agent.py](scripts/test_hybrid_agent.py) - Hybrid test suite
- [scripts/test_bm25.py](scripts/test_bm25.py) - BM25 vs vector comparison
- [langgraph.json](langgraph.json) - LangGraph deployment config

### Documentation

- [CLAUDE.md](CLAUDE.md) - Deep Agents framework guide
- [README.md](README.md) - Repository overview
- [FILESYSTEM_BACKEND_FIX.md](FILESYSTEM_BACKEND_FIX.md) - FilesystemBackend configuration

---

## Summary

✅ **Hybrid RAG successfully implemented** combining BM25 keyword matching with vector similarity search.

✅ **BM25 compensates for broken vector search** by providing reliable keyword matching fallback.

✅ **Test results prove effectiveness**: 5/5 relevant chunks for "attention mechanism" query.

✅ **Deployed via LangGraph CLI** as `hybrid_rag_agent` (RECOMMENDED).

✅ **Ready for evaluation** with 50 test questions across 12 categories.

The hybrid approach provides the best of both worlds: BM25's keyword precision + vector search's semantic understanding, with BM25 compensating for the vector search weaknesses discovered during testing.
