# CLAUDE.md - AI Assistant Guide

> **Project:** Agent-Harness-RAG - Comparing FileSearch vs Vector Store RAG
> **Last Updated:** 2025-11-24

## Project Overview

This repository is a **scientific evaluation framework** to compare two RAG approaches for document question-answering:

1. **FileSearch RAG** - Terminal-based (grep/glob) with exact keyword matching
2. **Vector Store RAG** - Semantic search with embeddings and reranking

**Objective:** Run 50 test questions through both systems, measure **Correctness**, **Latency**, and **Cost**, then make data-driven architecture decisions.

---

## System Architecture

### Our Setup (Local Infrastructure)

**LLM:**
- Model: Qwen/Qwen3-235B-A22B-Instruct-2507-FP8
- Endpoint: `http://10.26.1.56:8708/v1`
- Temperature: 0.7, Max Tokens: 8192

**Embeddings:**
- Model: Qwen/Qwen3-Embedding-8B
- Endpoint: `http://10.26.1.56:8786/v1/embeddings`

**Framework:**
- Deep Agents (LangChain + LangGraph)
- Middleware: TodoListMiddleware + FilesystemMiddleware
- Backend: FilesystemBackend (local disk)
- Deployment: Local LangGraph CLI

---

## The Two RAG Approaches

### 1. FileSearch RAG (Primary)

**Architecture:** See [AGENT_HARNESS.md](AGENT_HARNESS.md)

**How it works:**
- Uses filesystem tools: `grep`, `glob`, `read_file`, `ls`
- Exact keyword matching in documents
- No embedding or indexing required
- Direct file operations on `documents/` folder

**Workflow:**
```
Query → Plan with TodoList → Search with grep/glob → Read matching files → Generate answer
```

**Strengths:**
- ✅ Exact keyword precision
- ✅ Fast for specific terms
- ✅ Transparent search process
- ✅ Simple, no infrastructure overhead

**Best for:** Exact matches, structured queries, code/formula search

---

### 2. Vector Store RAG (Alternative)

**Architecture:** See [VECTOR_STORE_RAG.md](VECTOR_STORE_RAG.md)

**How it works:**
- ChromaDB vector store with local persistence
- Qwen embeddings for semantic search
- RecursiveCharacterTextSplitter (512 tokens, 50 overlap)
- Local reranking with BAAI/bge-reranker-base (no API)

**Workflow:**
```
Query → Embed → Vector search (k=20) → Rerank (n=5) → Generate answer
```

**Strengths:**
- ✅ Semantic understanding
- ✅ Handles synonyms, paraphrasing
- ✅ Natural language queries
- ✅ Scales to large corpus

**Best for:** Conceptual queries, semantic similarity, multi-hop reasoning

---

## Evaluation Framework

### 12 Question Categories (50 total questions)

See [evaluation/framework.md](evaluation/framework.md) for details.

1. **Exact Match / Keywords** (5) - "Find function `read_file`"
2. **Semantic Similarity** (6) - Different wording, same meaning
3. **Table & Structured Data** (4) - Extract from tables
4. **Formulas & Math** (4) - Equations and calculations
5. **Multi-hop Reasoning** (5) - Info from multiple sources
6. **Code Understanding** (4) - Find and explain code
7. **Acronyms & Abbreviations** (3) - "RAG" → "Retrieval-Augmented Generation"
8. **Contextual Disambiguation** (4) - Same word, different contexts
9. **Negation & Exclusion** (3) - "not", "without", "except"
10. **Temporal & Versioning** (3) - "What's new in latest version?"
11. **Factual Precision** (4) - Exact numbers, dates, names
12. **Conceptual / Abstract** (5) - "Why" and "how" questions

### 3 Evaluation Metrics

| Metric | What it measures |
|--------|------------------|
| **Correctness** | Is the answer factually correct? |
| **Latency** | Response time in seconds |
| **Cost per query** | Token usage and computation cost |

---

## Document Corpus

Located in `documents/`:
- `attention_is_all_you_need.pdf` - Transformer architecture paper
- `thinkpython2.pdf` - Python programming book
- `The Essence of Software Engineering, Volker Gruhn, Rudiger Striemer.pdf` - Software engineering
- `CLAUDE.md` - This file (can also be queried)

---

## Deep Agents Framework Essentials

Since both RAG approaches use Deep Agents, here are the key concepts:

### Core Components

**1. TodoListMiddleware** - Task planning
- Tool: `write_todos`
- Breaks complex queries into steps
- Tracks progress

**2. FilesystemMiddleware** - File operations
- Tools: `ls`, `read_file`, `write_file`, `edit_file`, `grep`, `glob`
- Manages context via files
- Prevents token overflow

**3. FilesystemBackend** - Storage
- Direct local disk operations
- Root directory: `./workspace` or project root
- Virtual mode for path sandboxing

### Data Flow

```
User Query
    ↓
Agent Plans (TodoList) - Break down task
    ↓
FileSearch OR Vector Search - Retrieve documents
    ↓
Read Files (Filesystem tools) - Extract content
    ↓
LLM Generation (Qwen 235B) - Synthesize answer
    ↓
Response with Citations
```

---

## When to Use Each RAG Approach

### Use FileSearch When:
✅ Query has specific keywords, codes, or exact terms
✅ Searching for structured data (tables, formulas, code)
✅ Corpus is small-medium (<10K documents)
✅ Speed and transparency are priorities
✅ No indexing overhead acceptable

### Use Vector Store When:
✅ Natural language, conceptual queries
✅ Need semantic understanding (synonyms, paraphrasing)
✅ Multi-hop reasoning across documents
✅ Large corpus (>10K documents)
✅ Varied query phrasing expected

### Use Hybrid When:
✅ Diverse query types
✅ Want best of both worlds
✅ Accuracy is top priority
✅ Can handle additional complexity

---

## AI Assistant Guidelines

### Understanding the Project

When helping with this codebase:

1. **Primary Goal:** Compare FileSearch vs Vector Store RAG objectively
2. **Method:** Scientific evaluation with 50 questions across 12 categories
3. **Output:** Data-driven recommendations on which approach to use
4. **Not Goal:** Build production RAG system yet (evaluation comes first)

### Working with RAG Architectures

**FileSearch RAG (AGENT_HARNESS.md):**
- Focus on grep/glob/read_file tools
- Terminal-based search patterns
- Direct file access strategies
- Keyword matching optimization

**Vector Store RAG (VECTOR_STORE_RAG.md):**
- ChromaDB setup and persistence
- Chunking strategies (512 tokens, 50 overlap)
- Local reranking with BAAI/bge-reranker-base
- Embedding management (Qwen3-Embedding-8B)

### Evaluation Framework (evaluation/framework.md)

When creating test questions:
- Follow the 12 category structure
- Ensure questions are answerable from corpus
- Consider both methods' strengths/weaknesses
- Include ground truth answers
- Specify expected difficulty

### Best Practices

**DO:**
- ✅ Reference specific architecture docs (AGENT_HARNESS.md, VECTOR_STORE_RAG.md)
- ✅ Consider evaluation categories when analyzing questions
- ✅ Measure Correctness, Latency, Cost for both approaches
- ✅ Provide objective comparisons with data
- ✅ Use local models (Qwen) - no external APIs

**DON'T:**
- ❌ Assume one approach is universally better
- ❌ Skip evaluation and jump to recommendations
- ❌ Ignore cost and latency (not just accuracy)
- ❌ Forget to cite sources in answers
- ❌ Use external APIs (everything runs locally)

### Common Tasks

**Analyzing Query Types:**
- Identify which category (1-12) a query belongs to
- Predict which RAG approach should perform better
- Explain reasoning based on architecture strengths

**Comparing Results:**
- Measure correctness, latency, cost for both methods
- Identify patterns in successes/failures
- Aggregate by category to find trends
- Recommend hybrid strategies if appropriate

**Optimizing Approaches:**
- Suggest improvements for FileSearch (better grep patterns, preprocessing)
- Suggest improvements for Vector Store (chunking, reranking, k values)
- Balance accuracy vs speed vs cost tradeoffs

---

## Environment Configuration

Environment variables in `.env`:

```bash
# LLM
LLM_BASE_URL=http://10.26.1.56:8708/v1
LLM_MODEL=Qwen/Qwen3-235B-A22B-Instruct-2507-FP8
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=8192

# Embeddings
EMBEDDINGS_BASE_URL=http://10.26.1.56:8786/v1/embeddings
EMBEDDINGS_MODEL=Qwen/Qwen3-Embedding-8B

# Storage
WORKSPACE_ROOT=./workspace
CHROMA_PERSIST_DIR=./chroma_db

# Retrieval
CHUNK_SIZE=512
CHUNK_OVERLAP=50
INITIAL_K=20
RERANK_TOP_N=5
RERANKER_MODEL=BAAI/bge-reranker-base
```

---

## Key References

### Project Documentation
- [README.md](README.md) - Project overview
- [AGENT_HARNESS.md](AGENT_HARNESS.md) - FileSearch RAG details
- [VECTOR_STORE_RAG.md](VECTOR_STORE_RAG.md) - Vector Store RAG details
- [evaluation/framework.md](evaluation/framework.md) - Evaluation methodology

### Deep Agents Framework
- [Deep Agents Overview](https://docs.langchain.com/oss/python/deepagents/overview)
- [Middleware Guide](https://docs.langchain.com/oss/python/deepagents/middleware)
- [Backends Guide](https://docs.langchain.com/oss/python/deepagents/backends)
- [Deep Agents Blog](https://blog.langchain.com/deep-agents/)

### RAG Best Practices
- [ChromaDB Integration](https://python.langchain.com/docs/integrations/vectorstores/chroma/)
- [Cross-Encoder Reranking](https://python.langchain.com/docs/integrations/document_transformers/cross_encoder_reranker/)
- [Chunking Research](https://research.trychroma.com/evaluating-chunking)
- [Hybrid Search Strategies](https://superlinked.com/vectorhub/articles/optimizing-rag-with-hybrid-search-reranking)

---

## Current Project Status

✅ **Complete:**
- FileSearch RAG architecture documented
- Vector Store RAG architecture documented
- Evaluation framework defined
- Document corpus organized
- Environment configuration ready

⏳ **Next:**
- Create 50 test questions across 12 categories
- Implement both RAG agents
- Run comparative evaluation
- Analyze results by category
- Generate recommendations

---

## Summary for AI Assistants

**This project:**
- Compares two RAG approaches scientifically
- Uses local Qwen models (no external APIs)
- Evaluates with 50 questions, 3 metrics, 12 categories
- Makes data-driven architecture decisions

**When assisting:**
- Reference architecture docs (AGENT_HARNESS.md, VECTOR_STORE_RAG.md)
- Consider evaluation framework (12 categories)
- Measure all 3 metrics (Correctness, Latency, Cost)
- Provide objective, evidence-based recommendations
- Help create test questions and run evaluations

**Key insight:** No single approach is universally better - we're discovering where each excels through systematic testing.
