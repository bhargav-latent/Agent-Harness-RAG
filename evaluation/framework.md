# Evaluation Framework: FileSearch vs Vector Store RAG

## Evaluation Metrics

We measure only 3 things:

| Metric | What it measures |
|--------|------------------|
| **Correctness** | Is the final answer factually correct? |
| **Latency** | How fast is the response? |
| **Cost per query** | How expensive is each query to run? |

---

## Question Categories

### 1. Exact Match / Keyword Search
Test finding specific terms, codes, identifiers, exact phrases.

**Example:** "Find the function named `read_file`"

---

### 2. Semantic Similarity
Test understanding meaning despite different wording, synonyms, paraphrasing.

**Example:** "How to prevent unauthorized access?" vs "Security best practices"

---

### 3. Table & Structured Data Retrieval
Test extracting information from tables, comparisons, matrices.

**Example:** "Compare StateBackend and StoreBackend"

---

### 4. Formulas & Mathematical Content
Test retrieving equations, calculations, algorithms.

**Example:** "What is the formula for attention scores?"

---

### 5. Multi-hop Reasoning
Test questions requiring information from multiple sources.

**Example:** "How do subagents use filesystem to maintain context isolation?"

---

### 6. Code Understanding
Test finding and explaining code snippets, patterns.

**Example:** "Show me code for creating a Deep Agent with RAG"

---

### 7. Acronyms & Abbreviations
Test bridging technical shorthand with full terminology.

**Example:** "What is RAG?" → should find "Retrieval-Augmented Generation"

---

### 8. Contextual Disambiguation
Test understanding same term in different contexts.

**Example:** "What is 'store'?" (backend vs. vector store vs. LangGraph Store)

---

### 9. Negation & Exclusion Queries
Test understanding "not", "without", "except", "excluding".

**Example:** "What backends don't support persistence?"

---

### 10. Temporal & Version Information
Test time-based queries, recency, version-specific.

**Example:** "What's new in the latest version?"

---

### 11. Factual Precision
Test exact facts: numbers, dates, names, specifications.

**Example:** "What is the token limit for GPT-4?"

---

### 12. Conceptual / Abstract Queries
Test high-level understanding, "why", "how", design rationale.

**Example:** "Why use subagents instead of a single agent?"

---

## Question Distribution

Total: **50 questions** across 12 categories

- Exact Match: 5 questions
- Semantic Similarity: 6 questions
- Table Data: 4 questions
- Formulas: 4 questions
- Multi-hop Reasoning: 5 questions
- Code Understanding: 4 questions
- Acronyms: 3 questions
- Contextual: 4 questions
- Negation: 3 questions
- Temporal: 3 questions
- Factual: 4 questions
- Conceptual: 5 questions
