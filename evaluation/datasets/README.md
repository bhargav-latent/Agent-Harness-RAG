# RAG Evaluation Datasets

This directory contains evaluation datasets for testing and benchmarking RAG (Retrieval-Augmented Generation) systems.

## Files

### evaluation_set.jsonl

**Format:** JSONL (JSON Lines) - one JSON object per line
**Size:** 43 KB
**Questions:** 50 total
**Created:** 2025-11-24

Complete evaluation dataset following the schema defined in [../dataset_schema.md](../dataset_schema.md).

## Dataset Statistics

### By Category (12 categories)

| Category | ID | Count | Percentage |
|----------|---|-------|------------|
| Exact Match / Keyword Search | exact_match | 5 | 10% |
| Semantic Similarity | semantic | 6 | 12% |
| Table & Structured Data | table_data | 4 | 8% |
| Formulas & Math | formulas | 4 | 8% |
| Multi-hop Reasoning | multi_hop | 5 | 10% |
| Code Understanding | code | 4 | 8% |
| Acronyms & Abbreviations | acronyms | 3 | 6% |
| Contextual Disambiguation | contextual | 4 | 8% |
| Negation & Exclusion | negation | 3 | 6% |
| Temporal & Version Info | temporal | 3 | 6% |
| Factual Precision | factual | 4 | 8% |
| Conceptual / Abstract | conceptual | 5 | 10% |

### By Difficulty

| Difficulty | Count | Percentage |
|-----------|-------|------------|
| Easy | 15 | 30% |
| Medium | 25 | 50% |
| Hard | 10 | 20% |

### By Source Document

| Document | Count | Percentage |
|----------|-------|------------|
| attention_is_all_you_need.md | 31 | 62% |
| thinkpython2.md | 13 | 26% |
| The Essence of Software Engineering... | 6 | 12% |

**Note:** Some questions (q022-q024, q033) span multiple documents for cross-document reasoning.

### By Reasoning Type

| Type | Count | Percentage |
|------|-------|------------|
| Single-hop | 41 | 82% |
| Multi-hop | 9 | 18% |

## Question ID Ranges

- **q001-q005:** Exact Match questions
- **q006-q011:** Semantic Similarity questions
- **q012-q015:** Table & Structured Data questions
- **q016-q019:** Formulas & Math questions
- **q020-q024:** Multi-hop Reasoning questions
- **q025-q028:** Code Understanding questions
- **q029-q031:** Acronyms questions
- **q032-q035:** Contextual Disambiguation questions
- **q036-q038:** Negation & Exclusion questions
- **q039-q041:** Temporal & Version Info questions
- **q042-q045:** Factual Precision questions
- **q046-q050:** Conceptual / Abstract questions

## Schema Fields

Each question contains:

### Core Fields
- `id` (string): Unique identifier (q001-q050)
- `question` (string): The user query
- `ground_truth` (string): Expected correct answer
- `category` (string): Question category
- `source_documents` (array): Source markdown files

### Metadata Object
- `difficulty` (string): "easy", "medium", or "hard"
- `expected_chunks` (array): Expected text passages to retrieve
- `reasoning_type` (string): "single-hop" or "multi-hop"

### Runtime Fields (to be added during evaluation)
- `retrieved_contexts` (array): Actually retrieved passages
- `answer` (string): RAG system's generated answer
- `metrics` (object): Evaluation scores
- `timestamp` (string): When evaluated

## Usage Examples

### Load with Python

```python
import json

# Load all questions
questions = []
with open('evaluation/datasets/evaluation_set.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        questions.append(json.loads(line))

print(f"Loaded {len(questions)} questions")

# Filter by category
exact_match_qs = [q for q in questions if q['category'] == 'exact_match']
print(f"Exact match questions: {len(exact_match_qs)}")

# Filter by difficulty
hard_qs = [q for q in questions if q['metadata']['difficulty'] == 'hard']
print(f"Hard questions: {len(hard_qs)}")
```

### Load with RAGAS

```python
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    context_recall,
    faithfulness,
    answer_relevancy
)
import json

# Load dataset
questions = []
with open('evaluation/datasets/evaluation_set.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        questions.append(json.loads(line))

# After running your RAG system and populating retrieved_contexts and answer fields...
# Convert to RAGAS format
ragas_dataset = {
    "question": [q["question"] for q in questions],
    "ground_truths": [[q["ground_truth"]] for q in questions],
    "contexts": [q["retrieved_contexts"] for q in questions],
    "answer": [q["answer"] for q in questions]
}

# Evaluate
results = evaluate(
    ragas_dataset,
    metrics=[context_precision, context_recall, faithfulness, answer_relevancy]
)

print(results)
```

### Sample a Subset

```python
import json
import random

# Load questions
with open('evaluation/datasets/evaluation_set.jsonl', 'r', encoding='utf-8') as f:
    questions = [json.loads(line) for line in f]

# Sample 10 random questions
sample = random.sample(questions, 10)

# Or stratified sample by difficulty
easy = [q for q in questions if q['metadata']['difficulty'] == 'easy']
medium = [q for q in questions if q['metadata']['difficulty'] == 'medium']
hard = [q for q in questions if q['metadata']['difficulty'] == 'hard']

stratified_sample = (
    random.sample(easy, 3) +
    random.sample(medium, 5) +
    random.sample(hard, 2)
)
```

## Validation

Validate the JSONL format:

```bash
# Check line count
wc -l evaluation_set.jsonl
# Should output: 50

# Validate JSON on each line
cat evaluation_set.jsonl | while read line; do echo "$line" | python -m json.tool > /dev/null || echo "Invalid JSON"; done

# Check for duplicate IDs
cat evaluation_set.jsonl | python -c "import json, sys; ids = [json.loads(l)['id'] for l in sys.stdin]; print('Duplicates:', len(ids) - len(set(ids)))"
```

## Key Features

✅ **Industry-Standard Format:** JSONL compatible with RAGAS, LangChain, and other RAG evaluation frameworks
✅ **Comprehensive Coverage:** 12 different question categories testing various RAG capabilities
✅ **Balanced Difficulty:** 30% easy, 50% medium, 20% hard
✅ **Multi-Document:** Includes cross-document reasoning questions
✅ **Rich Metadata:** Difficulty, expected chunks, reasoning type for detailed analysis
✅ **RAGAS Compatible:** Direct integration with RAGAS evaluation framework
✅ **Source Attribution:** Every question linked to source documents

## Cross-Document Questions

These questions specifically test multi-document retrieval and synthesis:

- **q022:** Iterative improvement (Think Python + Transformer paper)
- **q023:** Programming concepts + mathematical operations (Think Python + Transformer)
- **q024:** Software engineering principles + collaboration (Software Engineering + Transformer)
- **q033:** Context disambiguation across documents (Think Python + Transformer)

## Notes

- All source documents are in `rag_data/processed/`
- Ground truth answers are verified against source documents
- Expected chunks are actual text snippets from the documents
- Questions designed to test real RAG system capabilities
- Suitable for both FileSearch and Vector Store RAG evaluation

## Related Files

- [evaluation/framework.md](../framework.md) - Evaluation framework overview
- [evaluation/dataset_schema.md](../dataset_schema.md) - Complete schema documentation
- [rag_data/processed/](../../rag_data/processed/) - Source documents

## Citation

If using this dataset for research or benchmarking, please reference:

```
Agent-Harness-RAG Evaluation Dataset
50 questions across 12 categories for RAG system evaluation
Source: https://github.com/bhargav-latent/Agent-Harness-RAG
```
