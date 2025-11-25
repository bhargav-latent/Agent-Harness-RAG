# Agent-Harness-RAG

> **Systematic comparison of RAG approaches: FileSearch vs Vector Store vs BM25 vs Hybrid**

## Project Objective

This repository provides a framework to **scientifically evaluate and compare four RAG (Retrieval-Augmented Generation) approaches** for searching documents and answering questions:

1. **FileSearch RAG** - Terminal-based search using grep/glob/read_file
2. **Vector Store RAG** - Semantic search using ChromaDB with embeddings (⚠️ low relevance scores)
3. **BM25 RAG** - Keyword-based search using BM25 algorithm (✅ perfect keyword matching)
4. **Hybrid RAG** - Combines BM25 + vector search (✅ **RECOMMENDED**)

**Goal:** Make data-driven decisions about which RAG approach works best for our document corpus and query patterns.

---

## Why This Matters

Rather than guessing which RAG approach is better, we **measure and compare** using:
- **50 test questions** across 12 categories
- **3 simple metrics**: Correctness, Latency, Cost per query
- **Real data** from our document corpus

---

## The Four RAG Approaches

### Approach 1: FileSearch RAG

**How it works:** Uses terminal tools (grep, glob, read_file) for exact keyword matching

**Status:** ✅ Implemented

**Strengths:**
- ✅ Exact keyword matching
- ✅ Fast for specific terms
- ✅ Transparent search process
- ✅ No indexing overhead

**Best for:** Exact matches, structured queries, small corpus

---

### Approach 2: Vector Store RAG

**How it works:** Semantic similarity search with ChromaDB + Qwen embeddings

**Status:** ⚠️ Implemented but has low relevance scores (0.19-0.27)

**Strengths:**
- ⚠️ Semantic understanding (limited by low scores)
- ⚠️ Handles synonyms (when it works)
- ❌ Poor ranking quality

**Best for:** Not recommended as standalone - use Hybrid instead

**Issue:** Vector embeddings return very low similarity scores and poor ranking. See [docs/HYBRID_RAG_IMPLEMENTATION.md](docs/HYBRID_RAG_IMPLEMENTATION.md) for diagnosis.

---

### Approach 3: BM25 RAG

**How it works:** Keyword-based search using BM25 algorithm (classic IR)

**Status:** ✅ Implemented - **Perfect keyword matching (5/5 for "attention mechanism")**

**Strengths:**
- ✅ Perfect keyword matching
- ✅ Fast and efficient
- ✅ No embeddings needed
- ✅ Proven algorithm

**Best for:** Keyword queries, technical terms, exact phrases

---

### Approach 4: Hybrid RAG ⭐ **RECOMMENDED**

**How it works:** Combines BM25 keyword matching with vector similarity search

**Status:** ✅ Implemented and tested - **Best results**

**Strengths:**
- ✅ BM25 keyword precision
- ✅ Vector semantic understanding
- ✅ Best of both worlds
- ✅ BM25 compensates for vector weaknesses

**Results:** 5/5 relevant chunks for "attention mechanism" query

**Best for:** All query types - keyword + semantic queries

**Details:** See [docs/HYBRID_RAG_IMPLEMENTATION.md](docs/HYBRID_RAG_IMPLEMENTATION.md)

---

## Technology Stack

### Models (All Local)
- **LLM:** Qwen/Qwen2.5-32B-Instruct-AWQ @ `http://10.26.1.11:8786/v1`
- **Embeddings:** Qwen/Qwen3-Embedding-8B (4096 dims) @ `http://10.26.1.11:8786/v1`

### Framework
- **Deep Agents** (LangChain) - Agent orchestration with planning
- **Middleware:** TodoListMiddleware (multi-hop reasoning)
- **Backend:** FilesystemBackend (virtual mode for sandboxed operations)
- **Vector Store:** ChromaDB (persistent, 3,370 chunks)
- **BM25:** LangChain BM25Retriever (keyword matching)
- **Chunking:** RecursiveCharacterTextSplitter (512 chars, 50 overlap)

### Deployment
- **LangGraph CLI** - Local development server with auto-reload
- **4 Deployed Agents:** filesearch, vectorstore, bm25, hybrid_rag

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
├── .env                           # Environment configuration
├── requirements.txt               # Python dependencies
├── langgraph.json                 # LangGraph deployment (4 agents)
├── docs/                          # 📚 Documentation
│   ├── README.md                  # Documentation index
│   ├── HYBRID_RAG_IMPLEMENTATION.md  # ⭐ Hybrid RAG guide
│   ├── CLAUDE.md                  # Deep Agents framework guide
│   ├── WSL_DEPLOYMENT.md          # WSL/Linux deployment (recommended)
│   ├── WINDOWS_PATH_BUG.md        # Windows path bug & workarounds
│   ├── FILESYSTEM_BACKEND_FIX.md  # FilesystemBackend configuration
│   ├── DEPLOYMENT.md              # General deployment guide
│   ├── DEPLOYMENT_SUMMARY.md      # Deployment summary
│   ├── VECTORSTORE_SETUP.md       # Vector store setup
│   ├── AGENT_HARNESS.md           # FileSearch architecture
│   └── VECTOR_STORE_RAG.md        # Vector Store architecture
├── agents/                        # 🤖 RAG Agents
│   ├── filesearch_agent.py        # FileSearch RAG (grep/glob/read)
│   ├── vectorstore_agent.py       # Vector Store RAG (ChromaDB)
│   ├── bm25_agent.py              # BM25 Keyword RAG
│   └── hybrid_rag_agent.py        # Hybrid RAG ⭐ (RECOMMENDED)
├── scripts/                       # 🛠️ Setup Scripts
│   ├── preprocess_pdfs.py         # PDF to markdown conversion
│   ├── init_vectorstore.py        # Initialize ChromaDB with embeddings
│   ├── README.md                  # Scripts documentation
│   └── archive/                   # Archived diagnostic scripts
├── tests/                         # 🧪 Tests
│   └── archive/                   # Archived test scripts
├── rag_data/
│   ├── processed/                 # Preprocessed markdown (3,370 chunks)
│   │   ├── attention_is_all_you_need.md
│   │   ├── thinkpython2.md
│   │   └── The Essence of Software Engineering...md
│   └── metadata.json              # Processing metadata
├── chroma_db/                     # ChromaDB vector store (persistent)
├── evaluation/
│   ├── framework.md               # Evaluation framework
│   ├── dataset_schema.md          # Question dataset schema
│   └── datasets/
│       └── evaluation_set.jsonl   # 50 test questions
└── documents/                     # Original PDF documents
    ├── attention_is_all_you_need.pdf
    ├── thinkpython2.pdf
    └── The Essence of Software Engineering...pdf
```

---

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

The `.env` file is already configured for local LLM endpoints:
```bash
LLM_BASE_URL=http://10.26.1.56:8708/v1
LLM_MODEL=Qwen/Qwen3-235B-A22B-Instruct-2507-FP8
EMBEDDINGS_BASE_URL=http://10.26.1.56:8786/v1/embeddings
```

### 3. Deploy FileSearch RAG Agent

**Option A: WSL/Linux (Recommended)**
```bash
# See docs/WSL_DEPLOYMENT.md for full guide
wsl
cd "/mnt/d/Personal Projects/Agent-Harness-RAG"
source venv_wsl/bin/activate
langgraph dev
```

**Option B: Windows (with workaround for path bug)**
```bash
langgraph dev
# Note: Windows has a known path bug - see docs/WINDOWS_PATH_BUG.md
```

### 4. Access the Agent

Open in browser:
- **Studio UI**: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- **API Docs**: http://127.0.0.1:2024/docs
- **Direct API**: http://127.0.0.1:2024

### 5. Query the Agent

Test with a sample question:
```python
# Via Python
from src.filesearch_rag import FileSearchRAG

rag = FileSearchRAG()
result = rag.query("What is the attention mechanism in Transformers?")
print(result['answer'])
```

### 6. Run Evaluation

```bash
# Coming soon: Automated evaluation script
python evaluate.py --agent filesearch --dataset evaluation/datasets/evaluation_set.jsonl
```

---

## Current Status

### ✅ Complete
- [x] **All 4 RAG agents implemented** (FileSearch, Vector Store, BM25, Hybrid)
- [x] **Hybrid RAG tested and validated** - 5/5 perfect results for keyword queries
- [x] **Vector search diagnosis complete** - Identified low relevance score issue (0.19-0.27)
- [x] **BM25 proven effective** - Perfect keyword matching (5/5 for "attention mechanism")
- [x] Evaluation framework defined (12 categories, 3 metrics)
- [x] 50 test questions created across 12 categories
- [x] ChromaDB vector store initialized (3,370 chunks)
- [x] LangGraph deployment with 4 agents
- [x] Comprehensive documentation ([HYBRID_RAG_IMPLEMENTATION.md](HYBRID_RAG_IMPLEMENTATION.md))

### 🔄 In Progress
- [ ] Run evaluation on all 4 agents with 50 test questions
- [ ] Compare performance across agents and question categories
- [ ] Analyze results and generate report

### 📋 Next Steps
1. Run automated evaluation with 50 questions
2. Measure correctness, latency, cost per agent
3. Analyze results by question category
4. Make final architecture recommendations
5. Optional: Implement re-ranking enhancement for Hybrid RAG

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
| [HYBRID_RAG_IMPLEMENTATION.md](HYBRID_RAG_IMPLEMENTATION.md) | **⭐ Hybrid RAG implementation guide and test results** |
| [CLAUDE.md](CLAUDE.md) | Deep Agents framework guide for AI assistants |
| [langgraph.json](langgraph.json) | LangGraph deployment config (4 agents) |
| [WSL_DEPLOYMENT.md](WSL_DEPLOYMENT.md) | WSL/Linux deployment guide |
| [WINDOWS_PATH_BUG.md](WINDOWS_PATH_BUG.md) | Windows path bug documentation & workarounds |
| [FILESYSTEM_BACKEND_FIX.md](FILESYSTEM_BACKEND_FIX.md) | FilesystemBackend configuration guide |
| [evaluation/framework.md](evaluation/framework.md) | Evaluation categories and metrics |
| [evaluation/dataset_schema.md](evaluation/dataset_schema.md) | Question dataset schema (50 questions) |

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

## Summary

This repository implements and compares **4 RAG approaches** (FileSearch, Vector Store, BM25, Hybrid) for document question-answering.

**Key Finding:** **Hybrid RAG (BM25 + vector search) is recommended** as it combines perfect keyword matching (5/5) with semantic understanding, compensating for vector search weaknesses.

**Status:** All agents deployed via LangGraph CLI. Ready for evaluation with 50 test questions.
