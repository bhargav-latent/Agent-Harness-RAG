# Vector Store RAG Design Pattern

> **Alternative RAG approach using ChromaDB vector store with local reranking**

## Overview

This document describes the Vector Store RAG architecture using ChromaDB for semantic search, compared to the FileSearch terminal-based approach.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│           User Query                                 │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│           Query Embedding                            │
│     (Qwen/Qwen3-Embedding-8B)                       │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│      Vector Similarity Search                        │
│           (ChromaDB)                                 │
│     Retrieve top-k candidates (k=20)                │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│         Reranking (Optional)                         │
│    Local Cross-Encoder Model                        │
│  (BAAI/bge-reranker-base/large)                     │
│     Rerank to top-n results (n=5)                   │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│       Context + Query → LLM                          │
│        (Qwen 235B)                                   │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│           Generated Answer                           │
└─────────────────────────────────────────────────────┘
```

---

## Components

### 1. Vector Store: ChromaDB

**Why ChromaDB:**
- Lightweight and easy to set up
- Built-in persistence to disk
- Native LangChain integration
- Good for local development
- No external database server needed

**Configuration:**
```python
# Persistent ChromaDB (recommended for production)
persist_directory = "./chroma_db"

# In-memory ChromaDB (for testing only)
# Data lost when program ends
```

**LangChain Integration:**
- Full support via `langchain-chroma` package
- Direct retriever creation
- Supports metadata filtering
- Easy similarity search

**References:**
- [LangChain Chroma Integration](https://python.langchain.com/docs/integrations/vectorstores/chroma/)
- [Implementing RAG with Chroma](https://medium.com/@callumjmac/implementing-rag-in-langchain-with-chroma-a-step-by-step-guide-16fc21815339)
- [LangChain Chroma Tutorial](https://latenode.com/blog/langchain-chroma-integration-complete-vector-store-tutorial)

---

### 2. Embedding Model: Qwen3-Embedding-8B

**Configuration:**
- Model: Qwen/Qwen3-Embedding-8B
- Endpoint: `http://10.26.1.56:8786/v1/embeddings`
- Used for both indexing and query embedding

**Best Practices:**
- **Consistency:** Use same embedding model for indexing and querying
- **Token Limits:** Check model's max token limit (typically 512-8192)
- **Batch Processing:** Embed documents in batches for efficiency
- **Local Deployment:** Running locally avoids API costs

---

### 3. Document Preprocessing: Chunking Strategies

**Recommended Approach: RecursiveCharacterTextSplitter**

According to [Chroma Research](https://research.trychroma.com/evaluating-chunking) and [industry benchmarks](https://www.firecrawl.dev/blog/best-chunking-strategies-rag-2025):

**Best Configuration:**
- **Chunk Size:** 400-512 tokens
- **Chunk Overlap:** 50-100 tokens
- **Why:** Delivers 85-90% recall without computational overhead

**Chunking Method Options:**

1. **RecursiveCharacterTextSplitter** (Recommended)
   - Splits on paragraph, sentence, word boundaries
   - Preserves semantic coherence
   - Default choice for most use cases
   - **Best for:** General text, documentation

2. **Fixed-Size Chunking**
   - Simple equal-sized chunks
   - Fast but may break context
   - **Best for:** Uniform content

3. **Semantic Chunking**
   - Splits based on meaning/topics
   - Can improve recall by ~9%
   - More computationally expensive
   - **Best for:** Complex documents

4. **Page-Level Chunking**
   - Keep full pages intact
   - Won NVIDIA benchmarks (0.648 accuracy)
   - **Best for:** Structured documents (PDFs)

**LangChain Implementation:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)
```

**References:**
- [Chroma Chunking Evaluation](https://research.trychroma.com/evaluating-chunking)
- [Best Chunking Strategies 2025](https://www.firecrawl.dev/blog/best-chunking-strategies-rag-2025)
- [Mastering RAG Chunking](https://medium.com/@subhashbs36/mastering-rag-advanced-chunking-strategies-for-vector-databases-b6e2cbb042d3)

---

### 4. Retrieval Strategy

**Initial Retrieval: Similarity Search**
- Retrieve top-k documents (k=10-20)
- Uses cosine similarity on embeddings
- Fast vector search with approximate nearest neighbors

**Advanced: Hybrid Search** (Optional enhancement)

Combines two approaches:
1. **Dense Retrieval:** Vector similarity (semantic)
2. **Sparse Retrieval:** Keyword/BM25 (exact match)

**Why Hybrid:**
- Vector search: Good for semantic meaning, typos
- Keyword search: Better for exact terms, names, codes
- Combined: Best of both worlds

**Weighting:**
- α = 0.5: Equal weighting (common default)
- α = 0.7: Favor semantic search
- α = 0.3: Favor keyword search

**References:**
- [Optimizing RAG with Hybrid Search](https://superlinked.com/vectorhub/articles/optimizing-rag-with-hybrid-search-reranking)
- [Improving RAG with Hybrid Search](https://towardsdatascience.com/improving-retrieval-performance-in-rag-pipelines-with-hybrid-search-c75203c2f2f5/)
- [LangChain Retrieval Strategies](https://docs.langchain.com/oss/python/langchain/retrieval)

---

### 5. Reranking: Local Cross-Encoder Models

**Why Rerank:**
- Initial retrieval gets many candidates (k=20)
- Reranking selects best ones (n=5)
- Can dramatically improve recall performance
- More accurate than embedding models

**Local Models (No API Required):**

1. **BAAI/bge-reranker-base** (Recommended for speed)
   - 278M parameters
   - Fast inference
   - Good accuracy
   - Lower memory usage

2. **BAAI/bge-reranker-large** (Best accuracy)
   - 560M parameters
   - Higher accuracy
   - More memory intensive
   - Slower but better quality

3. **ms-marco-MiniLM-L-12-v2**
   - Smaller model
   - Very fast
   - Good for resource-constrained environments

**How Cross-Encoders Work:**
- Full-attention over query-document pairs
- More accurate than bi-encoders (embedding models)
- More time-consuming (use after initial retrieval)
- Runs locally without API calls

**LangChain Implementation:**
```python
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.retrievers import ContextualCompressionRetriever

# Load local cross-encoder model
cross_encoder = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-base")

# Create reranker compressor
compressor = CrossEncoderReranker(model=cross_encoder, top_n=5)

# Wrap base retriever with compression
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vector_store.as_retriever(search_kwargs={"k": 20})
)
```

**Process:**
1. Vector search retrieves top-20 candidates
2. Cross-encoder scores each candidate against query
3. Rerank and return top-5 most relevant
4. Pass to LLM for generation

**Benefits:**
- ✅ No external API calls
- ✅ Runs on local GPU/CPU
- ✅ Significantly improves retrieval quality
- ✅ Easy LangChain integration

**References:**
- [LangChain Cross-Encoder Reranker](https://python.langchain.com/docs/integrations/document_transformers/cross_encoder_reranker/)
- [BAAI/bge-reranker Models](https://huggingface.co/BAAI/bge-reranker-large)
- [Enhancing RAG with Reranking](https://medium.com/@myscale/enhancing-advanced-rag-systems-using-reranking-with-langchain-523a0b840311)

---

## Complete RAG Pipeline

### Stage 1: Document Indexing (One-time)

1. **Load Documents**
   - Extract text from PDFs
   - Load markdown files
   - Handle different formats

2. **Chunk Documents**
   - RecursiveCharacterTextSplitter
   - 512 tokens with 50 overlap
   - Preserve context at boundaries

3. **Generate Embeddings**
   - Use Qwen3-Embedding-8B
   - Batch process for efficiency
   - Store embeddings in ChromaDB

4. **Persist to Disk**
   - Save ChromaDB to `./chroma_db/`
   - Can reload without re-embedding

### Stage 2: Query Processing (Runtime)

1. **User Query**
   - Natural language question
   - No preprocessing needed

2. **Query Embedding**
   - Embed using same model (Qwen3-Embedding-8B)
   - Single embedding vector

3. **Initial Retrieval**
   - Vector similarity search in ChromaDB
   - Retrieve top-20 candidates
   - Fast approximate nearest neighbors

4. **Reranking** (Optional but recommended)
   - Score candidates with cross-encoder
   - Rerank to top-5 most relevant
   - Local model inference

5. **Context Construction**
   - Combine top-5 documents
   - Format with metadata/sources
   - Prepare prompt for LLM

6. **LLM Generation**
   - Send context + query to Qwen 235B
   - Generate answer with citations
   - Return to user

---

## Best Practices

### Document Preprocessing
✅ **Do:**
- Use RecursiveCharacterTextSplitter with 512 tokens
- Add 50-100 token overlap for context continuity
- Include metadata (filename, page, section)
- Persist ChromaDB to disk for production

❌ **Don't:**
- Use fixed-size chunks without overlap
- Exceed embedding model token limits
- Forget to include source attribution
- Use in-memory ChromaDB in production

### Retrieval Strategy
✅ **Do:**
- Start with k=20 initial retrieval
- Use reranking to narrow to top-5
- Test different k values for your data
- Consider hybrid search for mixed query types

❌ **Don't:**
- Retrieve too few candidates (k<10)
- Skip reranking if quality matters
- Use only vector search for exact matches
- Ignore retrieval metrics (precision/recall)

### Reranking
✅ **Do:**
- Use BAAI/bge-reranker-base as default
- Run locally without API calls
- Rerank after initial retrieval
- Monitor inference time

❌ **Don't:**
- Rerank too many documents (>50)
- Skip if retrieval quality is poor
- Use API-based rerankers (avoid cost/latency)
- Ignore GPU acceleration opportunities

---

## Vector Store vs FileSearch Comparison

| Aspect | Vector Store (ChromaDB) | FileSearch (grep/glob) |
|--------|------------------------|------------------------|
| **Strengths** | Semantic understanding, synonyms, concepts | Exact keywords, fast, transparent |
| **Search Type** | Approximate nearest neighbors | Exact string matching |
| **Setup Complexity** | Medium (indexing required) | Low (direct file access) |
| **Retrieval Speed** | Fast (with index) | Very fast (small corpus) |
| **Memory Usage** | Higher (embeddings + index) | Lower (no index) |
| **Query Flexibility** | Natural language, paraphrasing | Requires right keywords |
| **Maintenance** | Reindex on document changes | None (real-time) |
| **Best For** | Semantic queries, large corpus | Exact matches, structured queries |

---

## When to Use Vector Store RAG

✅ **Use Vector Store when:**
- Users ask natural language questions
- Need semantic understanding (synonyms, concepts)
- Corpus is large (>10K documents)
- Query phrasing varies widely
- Willing to invest in indexing setup

❌ **Stick with FileSearch when:**
- Need exact keyword matches
- Corpus is small (<1K documents)
- Queries are structured/specific
- Real-time document updates critical
- Minimize infrastructure complexity

---

## Recommended Configuration

### For Your Setup (Agent Harness)

```yaml
# Vector Store Configuration
vector_store: "chromadb"
persist_directory: "./chroma_db"

# Embedding
embedding_model: "Qwen/Qwen3-Embedding-8B"
embedding_url: "http://10.26.1.56:8786/v1/embeddings"

# Chunking
chunk_size: 512
chunk_overlap: 50
chunker: "RecursiveCharacterTextSplitter"

# Retrieval
initial_k: 20  # Initial candidates
rerank_top_n: 5  # After reranking

# Reranker
reranker_model: "BAAI/bge-reranker-base"
reranker_local: true  # No API calls

# Generation
llm_model: "Qwen/Qwen3-235B-A22B-Instruct-2507-FP8"
llm_url: "http://10.26.1.56:8708/v1"
```

---

## Implementation Path

### Phase 1: Basic Vector RAG
1. Set up ChromaDB with persistence
2. Implement RecursiveCharacterTextSplitter (512 tokens)
3. Index documents with Qwen embeddings
4. Basic similarity search retrieval
5. Test with evaluation framework

### Phase 2: Add Reranking
1. Install sentence-transformers locally
2. Integrate BAAI/bge-reranker-base
3. Add ContextualCompressionRetriever
4. Compare results with/without reranking

### Phase 3: Advanced (Optional)
1. Implement hybrid search (dense + sparse)
2. Tune k and rerank parameters
3. Add metadata filtering
4. Optimize for your query patterns

---

## Environment Variables

Add to `.env`:

```bash
# Vector Store
CHROMA_PERSIST_DIR=./chroma_db

# Chunking
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Retrieval
INITIAL_K=20
RERANK_TOP_N=5

# Reranker
RERANKER_MODEL=BAAI/bge-reranker-base
```

---

## Key References

### ChromaDB & LangChain
- [LangChain Chroma Integration](https://python.langchain.com/docs/integrations/vectorstores/chroma/)
- [RAG with LangChain and ChromaDB](https://medium.com/@tobintom/rag-with-langchain-and-chromadb-685e916ea4b4)
- [Building Production RAG Systems](https://www.tenxdeveloper.com/blog/building-a-production-ready-rag-system-with-langchain-and-chromadb)

### Chunking Strategies
- [Chroma Chunking Research](https://research.trychroma.com/evaluating-chunking)
- [Best Chunking Strategies 2025](https://www.firecrawl.dev/blog/best-chunking-strategies-rag-2025)
- [Databricks Chunking Guide](https://community.databricks.com/t5/technical-blog/the-ultimate-guide-to-chunking-strategies-for-rag-applications/ba-p/113089)

### Reranking
- [LangChain Cross-Encoder Reranker](https://python.langchain.com/docs/integrations/document_transformers/cross_encoder_reranker/)
- [BAAI BGE Reranker Models](https://huggingface.co/BAAI/bge-reranker-large)
- [Advanced RAG with Reranking](https://medium.com/@nadikapoudel16/advanced-rag-implementation-using-hybrid-search-reranking-with-zephyr-alpha-llm-4340b55fef22)

### Hybrid Search
- [Optimizing RAG with Hybrid Search](https://superlinked.com/vectorhub/articles/optimizing-rag-with-hybrid-search-reranking)
- [Improving RAG Pipelines](https://towardsdatascience.com/improving-retrieval-performance-in-rag-pipelines-with-hybrid-search-c75203c2f2f5/)
- [LangChain Retrieval Strategies](https://docs.langchain.com/oss/python/langchain/retrieval)

---

## Summary

**Vector Store RAG Pattern:**
- **Vector Store:** ChromaDB with local persistence
- **Embeddings:** Qwen3-Embedding-8B (your local model)
- **Chunking:** RecursiveCharacterTextSplitter (512 tokens, 50 overlap)
- **Retrieval:** Top-20 similarity search → Rerank to top-5
- **Reranker:** BAAI/bge-reranker-base (local, no API)
- **Generation:** Qwen 235B with retrieved context

**Key Advantages:**
- ✅ Semantic understanding of queries
- ✅ All processing local (no external APIs)
- ✅ LangChain native integration
- ✅ Reranking improves quality significantly
- ✅ Research-backed best practices
