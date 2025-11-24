# Agent-Harness-RAG

> **Systematic comparison of FileSearch vs Vector Store RAG for document question-answering**

## Project Objective

This repository provides a framework to **scientifically evaluate and compare two RAG (Retrieval-Augmented Generation) approaches** for searching documents and answering questions:

1. **FileSearch RAG** - Terminal-based search using grep/glob/read_file
2. **Vector Store RAG** - Semantic search using ChromaDB with embeddings

**Goal:** Make data-driven decisions about which RAG approach (or hybrid) works best for our document corpus and query patterns.

---

## Why This Matters

Rather than guessing which RAG approach is better, we **measure and compare** using:
- **50 test questions** across 12 categories
- **3 simple metrics**: Correctness, Latency, Cost per query
- **Real data** from our document corpus

---

## The Two Approaches

### Approach 1: FileSearch RAG (Current/Primary)

**How it works:** Uses terminal tools (grep, glob, read_file) for exact keyword matching

**Architecture:** [AGENT_HARNESS.md](AGENT_HARNESS.md)

**Strengths:**
- ✅ Exact keyword matching
- ✅ Fast for specific terms
- ✅ Transparent search process
- ✅ No indexing overhead

**Best for:** Exact matches, structured queries, small corpus

---

### Approach 2: Vector Store RAG (Alternative)

**How it works:** Semantic similarity search with embeddings and reranking

**Architecture:** [VECTOR_STORE_RAG.md](VECTOR_STORE_RAG.md)

**Strengths:**
- ✅ Semantic understanding
- ✅ Handles synonyms and paraphrasing
- ✅ Natural language queries
- ✅ Works at scale

**Best for:** Conceptual queries, large corpus, varied question phrasing

---

## Technology Stack

### Models (All Local)
- **LLM:** Qwen/Qwen3-235B-A22B-Instruct-2507-FP8 @ `http://10.26.1.56:8708/v1`
- **Embeddings:** Qwen/Qwen3-Embedding-8B @ `http://10.26.1.56:8786/v1/embeddings`

### Framework
- **Deep Agents** (LangChain) - Agent orchestration
- **Middleware:** TodoListMiddleware (planning) + FilesystemMiddleware (file ops)
- **Backend:** FilesystemBackend (local disk operations)
- **Vector Store:** ChromaDB (for Vector Store RAG)
- **Reranker:** BAAI/bge-reranker-base (local cross-encoder)

### Deployment
- **Local LangGraph CLI**

---

## Evaluation Framework

### 12 Question Categories (50 questions total)

| Category | Questions | Tests |
|----------|-----------|-------|
| Exact Match / Keywords | 5 | Finding specific terms, codes, identifiers |
| Semantic Similarity | 6 | Understanding meaning despite different wording |
| Table & Structured Data | 4 | Extracting from tables and comparisons |
| Formulas & Math | 4 | Retrieving equations and calculations |
| Multi-hop Reasoning | 5 | Synthesizing info from multiple sources |
| Code Understanding | 4 | Finding and explaining code patterns |
| Acronyms & Abbreviations | 3 | Bridging technical shorthand |
| Contextual Disambiguation | 4 | Same word, different contexts |
| Negation & Exclusion | 3 | Understanding "not", "without" |
| Temporal & Versioning | 3 | Time-based and version queries |
| Factual Precision | 4 | Exact numbers, dates, names |
| Conceptual / Abstract | 5 | High-level "why" and "how" questions |

**See:** [evaluation/framework.md](evaluation/framework.md)

---

### 3 Evaluation Metrics

| Metric | What it measures |
|--------|------------------|
| **Correctness** | Is the final answer factually correct? |
| **Latency** | How fast is the response? |
| **Cost per query** | How expensive is each query to run? |

---

## Repository Structure

```
Agent-Harness-RAG/
├── README.md                      # This file
├── CLAUDE.md                      # AI assistant guide
├── AGENT_HARNESS.md              # FileSearch RAG architecture
├── VECTOR_STORE_RAG.md           # Vector Store RAG architecture
├── .env.example                   # Environment configuration template
├── documents/                     # Document corpus
│   ├── attention_is_all_you_need.pdf
│   ├── thinkpython2.pdf
│   └── The Essence of Software Engineering...pdf
└── evaluation/                    # Evaluation framework
    └── framework.md              # Categories and metrics
```

---

## Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your endpoints
# LLM_BASE_URL=http://10.26.1.56:8708/v1
# EMBEDDINGS_BASE_URL=http://10.26.1.56:8786/v1/embeddings
```

### 2. Read the Documentation

- **FileSearch RAG:** [AGENT_HARNESS.md](AGENT_HARNESS.md)
- **Vector Store RAG:** [VECTOR_STORE_RAG.md](VECTOR_STORE_RAG.md)
- **Evaluation Framework:** [evaluation/framework.md](evaluation/framework.md)

### 3. Run Evaluation (Coming Soon)

1. Create 50 test questions based on categories
2. Build FileSearch agent
3. Build Vector Store agent
4. Run both on same questions
5. Compare: Correctness, Latency, Cost
6. Analyze results by category

---

## Current Status

### ✅ Complete
- [x] FileSearch RAG architecture documented
- [x] Vector Store RAG architecture documented
- [x] Evaluation framework defined (12 categories, 3 metrics)
- [x] Environment configuration
- [x] Document corpus organized

### 🔄 In Progress
- [ ] Create 50 test questions
- [ ] Implement FileSearch agent
- [ ] Implement Vector Store agent
- [ ] Run evaluation
- [ ] Analyze results

### 📋 Next Steps
1. Create test questions from documents
2. Build both RAG agents
3. Run comparative evaluation
4. Generate results report
5. Make architecture recommendations

---

## Expected Outcomes

### Questions to Answer

1. **Overall:** Which approach is better for our use case?
2. **By Category:** Where does FileSearch excel? Where does Vector Store win?
3. **Performance:** What are the speed/cost tradeoffs?
4. **Hybrid:** Should we combine both approaches?
5. **Optimization:** How can we improve each method?

### Decision Framework

Based on evaluation results, we'll decide:
- **Use FileSearch** - If exact matching and speed are priorities
- **Use Vector Store** - If semantic understanding is critical
- **Use Hybrid** - Combine both for best of both worlds
- **Optimize Current** - Improve FileSearch with better tools/strategies

---

## Key Documents

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview (this file) |
| [CLAUDE.md](CLAUDE.md) | AI assistant guide for this project |
| [AGENT_HARNESS.md](AGENT_HARNESS.md) | FileSearch RAG architecture details |
| [VECTOR_STORE_RAG.md](VECTOR_STORE_RAG.md) | Vector Store RAG architecture details |
| [evaluation/framework.md](evaluation/framework.md) | Evaluation categories and metrics |

---

## References

### Deep Agents Framework
- [Deep Agents Overview](https://docs.langchain.com/oss/python/deepagents/overview)
- [Deep Agents Blog Post](https://blog.langchain.com/deep-agents/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

### RAG Best Practices
- [ChromaDB Integration](https://python.langchain.com/docs/integrations/vectorstores/chroma/)
- [LangChain Reranking](https://python.langchain.com/docs/integrations/document_transformers/cross_encoder_reranker/)
- [Chunking Strategies Research](https://research.trychroma.com/evaluating-chunking)

---

## Contributing

This is a research/evaluation project. Contributions welcome for:
- Test question creation
- Agent implementations
- Evaluation improvements
- Documentation enhancements

---

## License

[Your License Here]

---

**Summary:** This repository systematically compares FileSearch vs Vector Store RAG to make evidence-based decisions about document retrieval architecture.
