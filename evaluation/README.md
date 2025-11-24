# Evaluation Framework for RAG Systems

> **Purpose:** Compare FileSearch RAG vs Vector Store RAG capabilities in the Agent-Harness-RAG system

## Overview

This evaluation framework provides a systematic approach to measure and compare the performance of two retrieval strategies:

1. **FileSearch (Text-based)** - Using tools like `grep`, `ripgrep`, keyword matching
2. **Vector Store (Semantic)** - Using embeddings and vector similarity search

## Framework Components

### 📁 Directory Structure

```
evaluation/
├── README.md                      # This file - Overview
├── framework.md                   # Detailed framework methodology
├── categories.md                  # Evaluation categories and criteria
├── metrics.md                     # Scoring rubrics and metrics
├── question_template.md           # Template for creating test questions
├── evaluation.py                  # Python framework implementation
├── questions/                     # Test question sets (to be created)
│   ├── exact_match.yaml
│   ├── semantic_similarity.yaml
│   ├── table_data.yaml
│   └── ... (one per category)
├── results/                       # Evaluation results (generated)
│   ├── filesearch_results.json
│   ├── vectorstore_results.json
│   └── comparison_report.html
└── scripts/                       # Helper scripts
    ├── run_evaluation.py
    ├── generate_report.py
    └── llm_judge.py
```

## Quick Start

### 1. Create Test Questions

```bash
# Use the question template to create questions for each category
# Store in evaluation/questions/ folder
```

### 2. Run Evaluation

```python
from evaluation.evaluation import EvaluationFramework

# Load questions
questions = load_questions("evaluation/questions/")

# Initialize framework
framework = EvaluationFramework(questions)

# Run both methods
results = framework.run_evaluation(
    filesearch_agent=my_filesearch_agent,
    vectorstore_agent=my_vectorstore_agent
)

# Generate report
framework.generate_report("evaluation/results/comparison_report.html")
```

### 3. Analyze Results

```bash
# View results
python evaluation/scripts/generate_report.py

# Opens HTML dashboard with:
# - Overall metrics comparison
# - Category-by-category breakdown
# - Individual question analysis
# - Performance characteristics
```

## Evaluation Categories (12 Total)

| Category | Questions | Purpose | Expected Winner |
|----------|-----------|---------|-----------------|
| **Exact Match / Keywords** | 5 | Test precision for specific terms | FileSearch |
| **Semantic Similarity** | 6 | Test understanding despite different wording | Vector Store |
| **Table & Structured Data** | 4 | Extract info from tables/matrices | FileSearch |
| **Formulas & Math** | 4 | Retrieve equations and calculations | FileSearch |
| **Multi-hop Reasoning** | 5 | Questions requiring multiple sources | Vector Store |
| **Code Understanding** | 4 | Find and explain code patterns | Both |
| **Acronyms & Abbreviations** | 3 | Bridge shorthand with full terms | Vector Store |
| **Contextual Disambiguation** | 4 | Same term, different contexts | Vector Store |
| **Negation & Exclusion** | 3 | Understand "not", "without" | Both |
| **Temporal & Versioning** | 3 | Time-based, recency queries | Both |
| **Factual Precision** | 4 | Exact numbers, dates, names | FileSearch |
| **Conceptual / Abstract** | 5 | High-level "why" and "how" | Vector Store |
| **TOTAL** | **50** | - | - |

See [categories.md](categories.md) for detailed definitions.

## Evaluation Metrics

### Per-Question Scores (0-5 scale each)

1. **Correctness** - Factual accuracy of the answer
2. **Completeness** - Coverage of all relevant aspects
3. **Relevance** - Answer addresses the question directly
4. **Citation Quality** - Source attribution and traceability

### Performance Metrics

- **Response Time** - Latency in seconds
- **Retrieved Doc Count** - Number of documents retrieved
- **Retrieved Doc Relevance** - Quality of retrieved documents

### Aggregate Metrics

- **Mean Score** - Average across all dimensions
- **Accuracy@K** - Percentage of correct answers
- **Win Rate** - Head-to-head comparison
- **Category Performance** - Breakdown by category
- **Latency Percentiles** - P50, P95, P99

See [metrics.md](metrics.md) for detailed scoring rubrics.

## Ground Truth Requirements

Each test question must include:

1. **Question text** - Natural language query
2. **Expected answer** - Ground truth response
3. **Expected sources** - Documents that should be retrieved
4. **Category** - Which evaluation category
5. **Difficulty** - 1-5 scale
6. **Evaluation criteria** - How to judge correctness

## Evaluation Methods

### Manual Evaluation
- Human expert reviews each answer
- Scores based on rubric
- Time-consuming but accurate

### LLM-as-Judge
- Use LLM to evaluate answers
- Compare to ground truth
- Faster, consistent, scalable

### Hybrid Approach (Recommended)
- LLM evaluates most questions
- Human review for disputed/complex cases
- Best balance of speed and accuracy

## Key Insights Expected

### FileSearch Strengths
✅ Exact keyword matching
✅ Structured data (tables, lists)
✅ Code and formula search
✅ Fast for specific terms
✅ Low infrastructure cost

### Vector Store Strengths
✅ Semantic understanding
✅ Synonym handling
✅ Multi-hop reasoning
✅ Conceptual queries
✅ Multi-language support

### Hybrid Opportunities
- Combine both for best results
- Use FileSearch for filtering
- Use Vector Store for ranking
- Adaptive strategy based on query type

## Usage Guidelines

### Creating Questions

1. **Diversity** - Cover all 12 categories
2. **Realism** - Real-world user queries
3. **Difficulty Range** - Easy to hard (1-5)
4. **Clear Ground Truth** - Unambiguous correct answers
5. **Source Attribution** - Know which docs contain answers

### Running Evaluations

1. **Consistency** - Same documents for both methods
2. **Fair Comparison** - Equal configuration (k=5, etc.)
3. **Multiple Runs** - Average over 3+ runs for stability
4. **Version Control** - Track question sets and results
5. **Reproducibility** - Document all parameters

### Interpreting Results

1. **No Single Winner** - Each method has strengths
2. **Category Analysis** - Where does each excel?
3. **Use Case Mapping** - Match method to user needs
4. **Cost Considerations** - Infrastructure vs accuracy
5. **Hybrid Strategy** - Best of both worlds

## Integration with Agent Harness

This framework integrates with Deep Agents:

```python
from deepagents import create_deep_agent
from evaluation.evaluation import EvaluationFramework

# Create FileSearch agent
filesearch_agent = create_deep_agent(
    model="gpt-4",
    tools=[grep, glob, read_file],
    system_prompt="Use filesystem tools for retrieval"
)

# Create Vector Store agent
vectorstore_agent = create_deep_agent(
    model="gpt-4",
    tools=[vector_search, read_file],
    system_prompt="Use vector search for semantic retrieval"
)

# Run evaluation
framework = EvaluationFramework(questions)
results = framework.compare(filesearch_agent, vectorstore_agent)
```

## Contributing

When adding new test questions:

1. Follow the [question_template.md](question_template.md)
2. Place in appropriate category file
3. Include ground truth and sources
4. Test with both methods before committing
5. Update category counts in this README

## References

- [Framework Methodology](framework.md) - Detailed evaluation approach
- [Category Definitions](categories.md) - All 12 categories explained
- [Metrics & Scoring](metrics.md) - Rubrics and calculations
- [Question Template](question_template.md) - How to create questions

## Versioning

- **v1.0** - Initial framework with 12 categories, 50 questions
- Questions and results are versioned separately
- Framework updates tracked in git history

---

**Next Steps:**
1. Create test questions using the template
2. Run initial baseline evaluation
3. Analyze results and iterate
4. Document findings and recommendations
