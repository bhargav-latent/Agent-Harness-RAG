# Agent-Harness-RAG

A comparative study of two RAG approaches: traditional hybrid retrieval (BM25 + vector search) versus agentic file search (LLM-controlled grep/glob/read tools). The experiment evaluates accuracy, latency, and token efficiency across 44 questions on a 3-document corpus.

---

## Quick Start

```bash
# Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Initialize vector store
python scripts/init_vectorstore.py

# Start LangGraph server
langgraph dev --port 2026

# Run benchmark
python src/benchmark_agents.py
```

### Configuration

```bash
# .env file
LLM_BASE_URL=http://10.26.1.56:8708/v1
LLM_MODEL=Qwen/Qwen3-235B-A22B-Instruct-2507-FP8
EMBEDDINGS_BASE_URL=http://10.26.1.11:8786/v1
```

---

## The Problem

Traditional RAG uses a fixed retrieval pipeline: embed the query, search a vector store, return top-k chunks. This works well for simple queries but struggles when:

- Information is scattered across multiple sections
- Tables or structured data need precise extraction
- The query requires iterative refinement to find relevant context

The alternative: give the LLM direct access to search tools (grep, glob, read_file) and let it decide how to retrieve information. This is the "agentic RAG" approach.

**Research question:** Does giving an LLM control over its own retrieval improve answer quality? At what cost?

---

## Architecture

### Two Agents, Same Corpus

Both agents use the same LLM (Qwen/Qwen3-235B), the same document corpus, and the same LangGraph harness. The only difference is retrieval strategy.

| Agent | Retrieval Strategy | Tools |
|-------|-------------------|-------|
| **hybrid_rag_agent** | Pre-computed BM25 + vector search | `hybrid_search`, `bm25_only_search`, `vector_only_search` |
| **filesearch_agent** | LLM-controlled file operations | `grep`, `glob`, `read_file`, `ls`, `write_todos`, `read_todos` |

### Hybrid RAG Agent

```
Query → BM25 (15 candidates) ──┐
                               ├→ Merge & Dedupe → Top 5 → LLM → Answer
Query → Vector Search (15) ────┘
```

**How it works:**
1. Query is sent to both BM25 and vector retrievers in parallel
2. Each returns 15 candidate chunks
3. Results are merged and deduplicated
4. Top 5 chunks are passed to the LLM for answer generation

**Why hybrid?** Our initial vector-only approach had poor recall:
```
Query: "attention mechanism"
Vector Search: 1/5 relevant (similarity score: 0.27)
BM25 Search:   5/5 relevant

Diagnosis: Embeddings producing low-quality similarity scores
Solution:  BM25 compensates for vector weakness
```

### FileSearch Agent (Agentic)

```
Query → Agent Plans (write_todos)
          ↓
        grep for keywords → read_file (line ranges)
          ↓
        Need more context? → grep again
          ↓
        Synthesize Answer
```

**How it works:**
1. Agent receives query and plans a search strategy
2. Uses `grep` to find files/lines containing relevant keywords
3. Uses `read_file` with specific line ranges to get context
4. Iterates: if answer is incomplete, searches again with refined queries
5. Synthesizes final answer from discovered content

**The harness:** LangGraph's Deep Agents framework provides:
- **TodoListMiddleware**: Planning capabilities (write_todos, read_todos)
- **FilesystemMiddleware**: Sandboxed file operations (grep, glob, read_file, ls)

### Document Corpus

| Document | Domain | Content |
|----------|--------|---------|
| attention_is_all_you_need.md | ML Research | Transformer paper |
| thinkpython2.md | Programming | Python textbook |
| The Essence of Software Engineering.md | Software Engineering | SE principles |

**Indexing:** 3,370 chunks (512 chars, 50 char overlap) in ChromaDB with Qwen3-Embedding-8B (4096 dims)

---

## Evaluation Methodology

### Dataset

44 questions across 11 categories, designed to stress-test different retrieval scenarios:

| Category | Count | What It Tests |
|----------|-------|---------------|
| exact_match | 5 | Finding specific terms, codes, identifiers |
| semantic | 6 | Understanding meaning despite different wording |
| table_data | 4 | Extracting from tables and structured data |
| formulas | 4 | Retrieving equations and mathematical content |
| multi_hop | 5 | Synthesizing info from multiple sources |
| acronyms | 3 | Bridging technical shorthand |
| contextual | 4 | Same word, different contexts |
| negation | 3 | Understanding "not", "without" |
| temporal | 3 | Time-based and version queries |
| factual | 4 | Exact numbers, dates, names |
| conceptual | 5 | High-level "why" and "how" questions |

#### Example Questions

**exact_match** (easy):
```json
{
  "question": "What is the value of dmodel used in the Transformer architecture?",
  "ground_truth": "The Transformer uses dmodel = 512 as the dimension for all sub-layers in the model, as well as the embedding layers."
}
```

**table_data** (medium):
```json
{
  "question": "Compare the computational complexity per layer between Self-Attention and Recurrent layers according to Table 1.",
  "ground_truth": "Self-Attention has complexity O(n²·d) per layer, while Recurrent layers have complexity O(n·d²) per layer."
}
```

**multi_hop** (hard):
```json
{
  "question": "How does the Transformer achieve better parallelization than recurrent models, and what is the computational trade-off?",
  "ground_truth": "Self-attention connects all positions with O(1) sequential operations vs O(n) for recurrent. Trade-off: O(n²·d) vs O(n·d²) complexity."
}
```

**negation** (hard):
```json
{
  "question": "What does the Transformer architecture NOT use, unlike previous state-of-the-art sequence models?",
  "ground_truth": "The Transformer does NOT use recurrence or convolution. It relies entirely on attention mechanisms."
}
```

### Scoring: LLM-as-Judge

The same LLM (Qwen3-235B) evaluates answer correctness against ground truth.

**Scoring rubric:**
| Score | Meaning |
|-------|---------|
| 5 | FULLY CORRECT: Accurate, complete, matches or exceeds ground truth |
| 4 | MOSTLY CORRECT: Factually correct with minor omissions |
| 3 | PARTIALLY CORRECT: Some correct info but significant gaps |
| 2 | MOSTLY WRONG: Major errors or misses the main point |
| 1 | COMPLETELY WRONG: Incorrect, irrelevant, or contradicts ground truth |

**Judge prompt:**
```
Evaluate the following RAG system answer against the ground truth.

## Question
{question}

## Ground Truth Answer (Expected)
{ground_truth}

## System Answer (To Evaluate)
{answer}

## Important Notes
- Focus on FACTUAL CORRECTNESS, not writing style
- Partial credit is acceptable
- The system answer doesn't need to be word-for-word identical
- Consider semantic equivalence (same meaning = correct)

Return: {"score": <1-5>, "explanation": "<reasoning>"}
```

**Judge parameters:** temperature=0.1 for consistent scoring

### Limitations of This Methodology

- **Same judge as answerer**: Using Qwen to judge Qwen's answers may introduce bias
- **Small dataset**: 44 questions may not be statistically significant
- **No confidence intervals**: Results are point estimates without error bars
- **Single run**: No repeated trials to measure variance

---

## Results

### Summary

| Metric | Hybrid RAG | FileSearch | Difference |
|--------|-----------|------------|------------|
| **Accuracy (mean)** | 4.20/5 | **4.67/5** | +11% |
| **Perfect scores (5/5)** | 53% | **80%** | +27pp |
| **Latency (median)** | **31s** | 58s | 1.9x slower |
| **Tokens (median)** | **12,137** | 37,294 | 3.1x more |
| **Tool calls (median)** | **2** | 6 | 3x more |

### Per-Category Breakdown

| Category | Hybrid | FileSearch | Winner | Notes |
|----------|--------|------------|--------|-------|
| table_data | 3.8 | **5.0** | FileSearch | Agent iterates to find exact rows |
| semantic | 4.2 | **5.0** | FileSearch | Multiple search attempts help |
| conceptual | 4.4 | **5.0** | FileSearch | Can gather broader context |
| temporal | **4.7** | 4.0 | Hybrid | Keywords like "2014 WMT" work well |
| negation | 3.3 | 3.7 | FileSearch | Both struggle |
| contextual | 3.5 | 3.8 | FileSearch | Both struggle |

### Outliers

Two queries caused runaway behavior in FileSearch (excluded from statistics):

| Query | Tokens | Time | Behavior |
|-------|--------|------|----------|
| q037 | 9M | 34 min | Iterative search loop |
| q045 | 9M | 14 min | Exhaustive document scan |

This highlights a risk of agentic approaches: without guardrails, agents can spiral into expensive loops.

---

## Key Findings

### When FileSearch Wins

1. **Scattered information**: Can grep, find a lead, then read surrounding context
2. **Tables and structured data**: Iterative reads find exact rows/columns
3. **Semantic understanding needed**: Multiple search attempts with refined queries

### When Hybrid Wins

1. **Keyword-based queries**: "dmodel = 512" just needs keyword matching
2. **Predictable retrieval**: Similar questions have similar patterns
3. **Cost-sensitive scenarios**: 3x fewer tokens at scale

### Shared Weaknesses

- **Negation queries**: "What is NOT mentioned?" requires knowing what's absent
- **Contextual disambiguation**: "What does 'function' mean in Python vs. Transformers?"
- **Cross-document reasoning**: Neither agent effectively synthesizes across all three documents

### Recommendation

| Scenario | Recommended Agent |
|----------|------------------|
| Production (cost-sensitive) | Hybrid RAG |
| High accuracy required | FileSearch |
| Tables/structured data | FileSearch |
| Simple factual queries | Hybrid RAG |
| High throughput needed | Hybrid RAG |

---

## Limitations & Future Work

### Current Limitations

- **No guardrails on FileSearch**: Agent can spiral into expensive loops
- **Small evaluation set**: 44 questions, especially few for negation/contextual
- **Single LLM**: Results may not generalize to other models
- **No statistical significance testing**: 4.20 vs 4.67 may be within noise
- **Chunking not optimized**: 512 chars with 50 overlap was not tuned

### Planned Improvements

**Guardrails:**
- Token/time limits to prevent runaway queries
- Maximum iteration count for agent loops

**Evaluation:**
- Larger dataset (especially hard categories)
- Multiple runs with different seeds
- Planning quality metrics, not just final answer

**Hybrid agent:**
- Combine pre-computed retrieval with agentic refinement
- Use fast retrieval first, escalate to agent when confidence is low

**Document processing:**
- Better PDF parsing to preserve tables and formulas
- Semantic chunking vs. fixed-size

---

## Repository Structure

```
Agent-Harness-RAG/
├── agents/
│   ├── hybrid_rag_agent.py      # BM25 + Vector hybrid
│   └── filesearch_agent.py      # Agentic file search
├── src/
│   ├── benchmark_agents.py      # Benchmark orchestrator
│   ├── langgraph_client.py      # LangGraph API client
│   └── llm_judge.py             # LLM-as-judge evaluator
├── evaluation/
│   ├── datasets/
│   │   └── evaluation_set.jsonl # 44 test questions
│   └── results/                 # Benchmark outputs
├── rag_data/
│   └── processed/               # Document corpus (markdown)
└── chroma_db/                   # Vector store
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| LLM | Qwen/Qwen3-235B-A22B-Instruct-2507-FP8 |
| Embeddings | Qwen/Qwen3-Embedding-8B (4096 dims) |
| Agent Framework | LangGraph + Deep Agents |
| Vector Store | ChromaDB |
| BM25 | LangChain BM25Retriever |
| Chunking | RecursiveCharacterTextSplitter (512 chars) |

---

## Contributing

Areas where contributions are welcome:

- **Evaluation dataset**: Add test questions, especially for negation/contextual
- **Guardrails**: Implement token/time limits for FileSearch agent
- **Hybrid agent**: Combine pre-computed retrieval with agentic refinement
- **Analysis**: Statistical significance testing, confidence intervals

---

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Deep Agents Overview](https://docs.langchain.com/oss/python/deepagents/overview)
- [ChromaDB Integration](https://python.langchain.com/docs/integrations/vectorstores/chroma/)
- [BM25 Retriever](https://python.langchain.com/docs/integrations/retrievers/bm25/)

---

## License

MIT License
