# RAG Evaluation Dataset Schema

## Overview

This document defines the schema for our RAG evaluation dataset. The format balances industry best practices with simplicity and relevance to our Deep Agents RAG system.

## Design Principles

1. **Simple & Practical** - Easy to create, read, and maintain
2. **RAGAS Compatible** - Works with standard RAG evaluation frameworks
3. **Comprehensive** - Supports all 12 question categories in our framework
4. **Measurable** - Enables tracking of Correctness, Latency, and Cost

---

## Data Format

**File Format:** JSONL (JSON Lines)
- One JSON object per line
- Easy to stream and process
- Human-readable
- Compatible with most RAG evaluation tools

**File Location:** `evaluation/datasets/evaluation_set.jsonl`

---

## Schema Definition

### Core Fields (Required)

```json
{
  "id": "string",                    // Unique identifier (e.g., "q001")
  "question": "string",              // The user query
  "ground_truth": "string",          // The correct/expected answer
  "category": "string",              // Category from framework (1-12)
  "source_documents": ["string"],    // Which docs contain the answer
  "metadata": {                      // Additional context
    "difficulty": "string",          // "easy", "medium", "hard"
    "expected_chunks": ["string"],   // Expected text passages to retrieve
    "reasoning_type": "string"       // "single-hop", "multi-hop"
  }
}
```

### Runtime Fields (Added During Evaluation)

```json
{
  "retrieved_contexts": ["string"],  // Actually retrieved passages
  "answer": "string",                // RAG system's generated answer
  "metrics": {
    "correctness": 0.0,              // 0-1 score
    "latency_ms": 0,                 // Response time in milliseconds
    "cost_usd": 0.0,                 // Cost per query
    "context_precision": 0.0,        // RAGAS metric
    "context_recall": 0.0,           // RAGAS metric
    "answer_relevancy": 0.0,         // RAGAS metric
    "faithfulness": 0.0              // RAGAS metric
  },
  "timestamp": "ISO-8601"            // When evaluated
}
```

---

## Category Mapping

Based on [evaluation/framework.md](framework.md):

| Category ID | Category Name | Question Count |
|------------|---------------|----------------|
| `exact_match` | Exact Match / Keyword Search | 5 |
| `semantic` | Semantic Similarity | 6 |
| `table_data` | Table & Structured Data | 4 |
| `formulas` | Formulas & Math | 4 |
| `multi_hop` | Multi-hop Reasoning | 5 |
| `code` | Code Understanding | 4 |
| `acronyms` | Acronyms & Abbreviations | 3 |
| `contextual` | Contextual Disambiguation | 4 |
| `negation` | Negation & Exclusion | 3 |
| `temporal` | Temporal & Version Info | 3 |
| `factual` | Factual Precision | 4 |
| `conceptual` | Conceptual / Abstract | 5 |

**Total:** 50 questions

---

## Source Documents

Our evaluation questions will draw from these processed documents:

1. **attention_is_all_you_need.md** - Transformer architecture paper
2. **The Essence of Software Engineering...md** - Software engineering textbook
3. **thinkpython2.md** - Python programming book

---

## Example Samples

### Example 1: Exact Match (Easy)

```json
{
  "id": "q001",
  "question": "What is the dimension dmodel used in the Transformer model?",
  "ground_truth": "The Transformer model uses dmodel = 512 as the dimension for all sub-layers and embedding layers.",
  "category": "exact_match",
  "source_documents": ["attention_is_all_you_need.md"],
  "metadata": {
    "difficulty": "easy",
    "expected_chunks": ["Encoder: The encoder is composed of a stack of N = 6 identical layers...produce outputs of dimension dmodel = 512"],
    "reasoning_type": "single-hop"
  }
}
```

### Example 2: Multi-hop Reasoning (Hard)

```json
{
  "id": "q025",
  "question": "How does the Transformer achieve parallelization compared to recurrent models, and what is the computational complexity benefit?",
  "ground_truth": "The Transformer achieves parallelization by using self-attention layers instead of recurrent layers. Self-attention connects all positions with O(1) sequential operations, while recurrent layers require O(n) sequential operations. The computational complexity is O(n²·d) for self-attention versus O(n·d²) for recurrent layers, making self-attention faster when sequence length n is smaller than representation dimension d.",
  "category": "multi_hop",
  "source_documents": ["attention_is_all_you_need.md"],
  "metadata": {
    "difficulty": "hard",
    "expected_chunks": [
      "self-attention layer connects all positions with a constant number of sequentially executed operations",
      "recurrent layer requires O(n) sequential operations",
      "computational complexity table showing comparison"
    ],
    "reasoning_type": "multi-hop"
  }
}
```

### Example 3: Code Understanding (Medium)

```json
{
  "id": "q040",
  "question": "Show an example of how to create a simple function in Python and call it.",
  "ground_truth": "To create and call a function in Python:\n\n```python\ndef greet(name):\n    print(f'Hello, {name}!')\n\ngreet('World')  # Outputs: Hello, World!\n```\n\nYou define a function using 'def', followed by the function name, parameters in parentheses, and a colon. The function body is indented.",
  "category": "code",
  "source_documents": ["thinkpython2.md"],
  "metadata": {
    "difficulty": "medium",
    "expected_chunks": ["function definition syntax", "function calling examples"],
    "reasoning_type": "single-hop"
  }
}
```

### Example 4: Semantic Similarity (Medium)

```json
{
  "id": "q010",
  "question": "What mechanism allows the Transformer to understand word order without using recurrence?",
  "ground_truth": "The Transformer uses positional encodings to inject information about the relative or absolute position of tokens in the sequence. These positional encodings use sine and cosine functions of different frequencies and are added to the input embeddings at the bottoms of the encoder and decoder stacks.",
  "category": "semantic",
  "source_documents": ["attention_is_all_you_need.md"],
  "metadata": {
    "difficulty": "medium",
    "expected_chunks": ["positional encoding section", "sine and cosine functions"],
    "reasoning_type": "single-hop"
  }
}
```

---

## Difficulty Levels

### Easy
- Single fact lookup
- Explicit information in text
- No reasoning required
- Example: "What is the value of X?"

### Medium
- Requires understanding context
- May need to connect 2-3 related sentences
- Light reasoning or synthesis
- Example: "How does X work?"

### Hard
- Multi-hop reasoning
- Synthesis across multiple sections/documents
- Complex relationships
- Example: "Compare X and Y, and explain why Z is used"

---

## Dataset Statistics (Target)

```
Total Questions: 50

By Category:
- Exact Match: 5 (10%)
- Semantic: 6 (12%)
- Table Data: 4 (8%)
- Formulas: 4 (8%)
- Multi-hop: 5 (10%)
- Code: 4 (8%)
- Acronyms: 3 (6%)
- Contextual: 4 (8%)
- Negation: 3 (6%)
- Temporal: 3 (6%)
- Factual: 4 (8%)
- Conceptual: 5 (10%)

By Difficulty:
- Easy: ~15 (30%)
- Medium: ~25 (50%)
- Hard: ~10 (20%)

By Document:
- attention_is_all_you_need.md: ~20 questions
- Software Engineering book: ~15 questions
- thinkpython2.md: ~15 questions
```

---

## RAGAS Integration

Our schema is fully compatible with RAGAS evaluation framework:

```python
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    context_recall,
    faithfulness,
    answer_relevancy
)

# Load dataset
dataset = load_evaluation_dataset("evaluation/datasets/evaluation_set.jsonl")

# Convert to RAGAS format
ragas_dataset = {
    "question": [item["question"] for item in dataset],
    "ground_truths": [[item["ground_truth"]] for item in dataset],
    "contexts": [item["retrieved_contexts"] for item in dataset],
    "answer": [item["answer"] for item in dataset]
}

# Evaluate
results = evaluate(
    ragas_dataset,
    metrics=[
        context_precision,
        context_recall,
        faithfulness,
        answer_relevancy
    ]
)
```

---

## Best Practices

### Question Writing

1. **Be Specific** - Avoid ambiguous questions
2. **Match Real Use Cases** - Reflect actual user queries
3. **Vary Complexity** - Mix easy, medium, hard questions
4. **Include Edge Cases** - Test system boundaries
5. **Natural Language** - Write as users would ask

### Ground Truth Writing

1. **Be Complete** - Include all necessary information
2. **Be Accurate** - Verify against source documents
3. **Be Concise** - No unnecessary elaboration
4. **Include Context** - When needed for clarity
5. **Cite Sources** - Reference specific passages when possible

### Expected Chunks

1. **Be Precise** - Include exact text snippets when possible
2. **Be Minimal** - Only essential passages
3. **Be Relevant** - Directly answers the question
4. **Multiple Options** - List alternative valid retrievals if applicable

---

## Validation Checklist

Before finalizing the dataset:

- [ ] All required fields present
- [ ] IDs are unique and sequential
- [ ] Questions are clear and unambiguous
- [ ] Ground truths are verified against source documents
- [ ] Categories match framework definitions
- [ ] Difficulty levels are appropriate
- [ ] Distribution matches targets (50 total, correct category counts)
- [ ] JSONL format is valid (one object per line)
- [ ] Source documents exist and are referenced correctly
- [ ] Expected chunks are accurate excerpts from source docs

---

## References

Based on industry best practices and research:

- [RAGAS Evaluation Framework](https://docs.ragas.io/en/stable/concepts/components/eval_dataset/)
- [RAG Evaluation Best Practices 2025](https://orq.ai/blog/rag-evaluation)
- [LangChain RAG Evaluation Guide](https://docs.smith.langchain.com/evaluation/tutorials/rag)
- [RAGEval Dataset Generation](https://arxiv.org/abs/2408.01262)

---

## Next Steps

1. ✅ Define schema (this document)
2. ⏭️ Generate 50 questions across 12 categories
3. ⏭️ Validate questions against source documents
4. ⏭️ Create generation script for automated dataset creation
5. ⏭️ Integrate with RAGAS evaluation pipeline
