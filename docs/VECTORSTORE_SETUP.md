# Vector Store RAG Agent - Setup Guide

## Overview

The Vector Store RAG agent uses semantic similarity search via ChromaDB and embeddings to retrieve relevant document chunks. This approach is particularly good for:

- Conceptual questions and exploratory queries
- Finding semantically related content even with different wording
- Questions that benefit from understanding context and relationships

## Prerequisites

### 1. Embeddings Endpoint

The vector store requires an embeddings API endpoint to generate vector embeddings for documents and queries.

**Current Configuration** (`.env`):
```bash
EMBEDDINGS_BASE_URL=http://10.26.1.56:8786/v1/embeddings
EMBEDDINGS_MODEL=Qwen/Qwen3-Embedding-8B
```

### 2. Network Connectivity

**Important**: The embeddings endpoint must be accessible from your machine.

**Test Connectivity**:
```bash
curl http://10.26.1.56:8786/v1/embeddings
```

If you get "Connection refused", the endpoint is not accessible:
- **On Windows**: May need VPN or network configuration
- **On WSL/Linux**: Usually has better network access to internal endpoints
- **Alternative**: Use a different embeddings endpoint or run locally

## Setup Steps

### Option 1: WSL/Linux (Recommended)

If the embeddings endpoint is not accessible from Windows, use WSL:

```bash
# Open WSL
wsl

# Navigate to project
cd "/mnt/d/Personal Projects/Agent-Harness-RAG"

# Activate virtual environment
source venv_wsl/bin/activate

# Initialize vector store
python scripts/init_vectorstore.py

# Run LangGraph server
langgraph dev
```

**Advantages**:
- Better network connectivity to internal endpoints
- No Windows path bugs
- Full compatibility

### Option 2: Windows (if endpoint accessible)

```bash
# Test connectivity first
curl http://10.26.1.56:8786/v1/embeddings

# If successful, initialize vector store
python scripts/init_vectorstore.py

# Run LangGraph server (will detect both agents)
langgraph dev
```

### Option 3: Alternative Embeddings

If you cannot access the configured endpoint, you can:

1. **Use Local Embeddings** (Sentence Transformers):
   ```python
   from langchain_community.embeddings import HuggingFaceEmbeddings

   embeddings = HuggingFaceEmbeddings(
       model_name="sentence-transformers/all-mpnet-base-v2"
   )
   ```

2. **Use OpenAI Embeddings**:
   ```python
   from langchain_openai import OpenAIEmbeddings

   embeddings = OpenAIEmbeddings(
       model="text-embedding-3-small",
       api_key="your-openai-api-key"
   )
   ```

3. **Modify `scripts/init_vectorstore.py`** to use the alternative embeddings model

## Vector Store Initialization

### What It Does

The initialization script (`scripts/init_vectorstore.py`):

1. **Loads Documents**: Reads all `.md` files from `rag_data/processed/`
2. **Chunks Documents**: Splits into 512-character chunks with 50-character overlap
3. **Generates Embeddings**: Creates vector embeddings for each chunk
4. **Stores in ChromaDB**: Persists vectors to `./chroma_db/`
5. **Tests Retrieval**: Runs a sample query to verify functionality

### Expected Output

```
================================================================================
INITIALIZING VECTOR STORE
================================================================================

Documents directory: ./rag_data/processed
ChromaDB directory: ./chroma_db
Chunk size: 512
Chunk overlap: 50

Step 1: Loading markdown documents...
[OK] Loaded 3 documents
  - attention_is_all_you_need.md: 46892 characters
  - thinkpython2.md: 508844 characters
  - The Essence of Software Engineering...md: 677549 characters

Step 2: Splitting documents into chunks...
[OK] Created 3370 chunks
  - Average chunk size: 375 characters
  - Min chunk size: 16 characters
  - Max chunk size: 511 characters

Step 3: Initializing embedding model...
[OK] Using embeddings endpoint: http://10.26.1.56:8786/v1/embeddings
  Model: Qwen/Qwen3-Embedding-8B

Step 4: Creating ChromaDB vector store...
[...] Generating embeddings and storing vectors (this may take a while)...
[OK] Vector store created with 3370 embeddings
  Persisted to: ./chroma_db

Step 5: Testing vector store retrieval...
[OK] Test query: 'What is the attention mechanism?'
  Retrieved 3 documents:
  1. attention_is_all_you_need.md: ...
  2. attention_is_all_you_need.md: ...
  3. attention_is_all_you_need.md: ...

================================================================================
[SUCCESS] VECTOR STORE INITIALIZED SUCCESSFULLY
================================================================================

Vector store is ready for use!
```

### Initialization Time

Expect **5-15 minutes** depending on:
- Number of chunks (3370 for current corpus)
- Embeddings endpoint speed
- Network latency

## Using the Vector Store Agent

### Via LangGraph CLI

Once initialized, the vector store agent is available via LangGraph CLI:

```bash
langgraph dev
```

**Access**:
- Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- Select: `vectorstore_agent` from the dropdown
- API Docs: http://127.0.0.1:2024/docs

### Via Python

```python
from src.vectorstore_rag import VectorStoreRAG

# Initialize agent
rag = VectorStoreRAG()

# Query
result = rag.query("What is the attention mechanism?")
print(result['answer'])
```

## Agent Capabilities

### Tools Available

1. **`vector_search(query, k=5)`**
   - Semantic similarity search
   - Returns top-k most relevant document chunks
   - Good for: Most queries, exploratory questions

2. **`vector_search_with_scores(query, k=5)`**
   - Same as vector_search but includes relevance scores
   - Scores range from 0 (irrelevant) to 1 (highly relevant)
   - Good for: Understanding search quality, debugging

### Query Examples

**Conceptual Question**:
```
Query: "What is self-attention and how does it differ from recurrent approaches?"
Agent will:
1. vector_search("self-attention recurrent RNN comparison", k=5)
2. Analyze retrieved chunks from attention paper
3. Synthesize answer with citations
```

**Code Question**:
```
Query: "How do I create a dictionary in Python?"
Agent will:
1. vector_search("create dictionary Python dict", k=3)
2. Find relevant sections from Think Python
3. Provide code examples with explanations
```

## Comparing FileSearch vs Vector Store

### FileSearch Agent

**Strengths**:
- Exact keyword matching
- Can read entire files
- Grep for specific terms
- Good for: Known terminology, specific facts, code symbols

**Weaknesses**:
- No semantic understanding
- Misses synonyms and paraphrases
- Requires knowing exact terms

### Vector Store Agent

**Strengths**:
- Semantic similarity matching
- Finds conceptually related content
- Handles synonyms and paraphrases
- Good for: Conceptual questions, exploratory queries

**Weaknesses**:
- May miss exact keyword matches
- Chunking can split related content
- No context beyond chunk boundaries

### When to Use Each

| Question Type | Best Agent | Why |
|--------------|------------|-----|
| "What is d_model in Transformers?" | FileSearch | Exact term search |
| "How do attention mechanisms work?" | Vector Store | Conceptual understanding |
| "Find all uses of self.attention" | FileSearch | Code symbol search |
| "Explain the key ideas in the paper" | Vector Store | Semantic overview |
| "What's on page 5 of the PDF?" | FileSearch | File structure navigation |
| "Compare X and Y approaches" | Vector Store | Conceptual comparison |

## Troubleshooting

### Issue: Connection Refused to Embeddings Endpoint

**Symptom**: `openai.APIConnectionError: Connection error`

**Solutions**:
1. **Use WSL**: Better network connectivity to internal endpoints
2. **Check VPN**: Ensure you're on the correct network
3. **Alternative Embeddings**: Use local Sentence Transformers
4. **Test Connectivity**: `curl http://10.26.1.56:8786/v1/embeddings`

### Issue: ChromaDB Not Found

**Symptom**: `No such file or directory: './chroma_db'`

**Solution**: Run `python scripts/init_vectorstore.py` first

### Issue: Agent Can't Find Documents

**Symptom**: `vector_search` returns "No relevant documents found"

**Solutions**:
1. Verify vector store is initialized: `ls chroma_db/`
2. Check embeddings compatibility
3. Try different search queries
4. Increase k parameter: `vector_search(query, k=10)`

### Issue: Slow Initialization

**Symptom**: Script takes very long (>30 minutes)

**Solutions**:
1. Check network latency to embeddings endpoint
2. Consider reducing chunk count in `.env`:
   ```bash
   CHUNK_SIZE=1024  # Larger chunks = fewer embeddings
   ```
3. Use WSL/Linux for better performance
4. Use local embeddings (faster, no network)

## Configuration Options

### `.env` Settings

```bash
# Embeddings
EMBEDDINGS_BASE_URL=http://10.26.1.56:8786/v1/embeddings
EMBEDDINGS_MODEL=Qwen/Qwen3-Embedding-8B

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_db

# Chunking Strategy
CHUNK_SIZE=512              # Characters per chunk
CHUNK_OVERLAP=50            # Overlap between chunks

# Retrieval
TOP_K_RETRIEVAL=20          # Chunks to retrieve initially
TOP_N_RERANK=5              # Chunks after reranking
RERANKER_MODEL=BAAI/bge-reranker-base
```

### Chunking Strategy

Current: **512 characters with 50 overlap**

**Trade-offs**:
- **Smaller chunks** (256-512): More precise retrieval, more chunks
- **Larger chunks** (1024-2048): More context, fewer chunks, less precise

**Adjust Based On**:
- Document structure (code vs prose)
- Query types (specific vs general)
- Performance requirements

## Next Steps

1. **Initialize Vector Store**: `python scripts/init_vectorstore.py`
2. **Deploy Agent**: `langgraph dev`
3. **Test Queries**: Compare with FileSearch agent
4. **Run Evaluation**: Use 50 test questions to measure performance
5. **Optimize**: Adjust chunking and retrieval parameters based on results

---

**Status**: Vector Store RAG agent is implemented and ready to deploy once embeddings endpoint is accessible or alternative embeddings are configured.
