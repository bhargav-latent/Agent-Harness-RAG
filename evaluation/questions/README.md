# Test Questions Directory

This directory contains the test question sets for RAG evaluation.

## Structure

Questions are organized by category, one YAML file per category:

```
questions/
├── exact_match.yaml           # 5 questions - Exact keyword matching
├── semantic_similarity.yaml   # 6 questions - Understanding despite different wording
├── table_data.yaml           # 4 questions - Structured data extraction
├── formulas.yaml             # 4 questions - Mathematical content retrieval
├── multi_hop_reasoning.yaml  # 5 questions - Cross-document synthesis
├── code_understanding.yaml   # 4 questions - Code search and explanation
├── acronyms.yaml             # 3 questions - Acronym/abbreviation handling
├── contextual.yaml           # 4 questions - Contextual disambiguation
├── negation.yaml             # 3 questions - Negation and exclusion
├── temporal.yaml             # 3 questions - Time and version queries
├── factual.yaml              # 4 questions - Precise factual information
└── conceptual.yaml           # 5 questions - Abstract and conceptual queries
```

## Total: 50 Questions

## Creating Questions

1. Use the [question_template.md](../question_template.md) as a guide
2. Follow the YAML format specified
3. Include all required fields:
   - question_id, category, difficulty
   - question_text
   - expected_answer
   - expected_sources
   - evaluation_criteria
4. Ensure ground truth is accurate and verifiable
5. Test questions with both FileSearch and Vector Store before finalizing

## Status

- [ ] exact_match.yaml (0/5 questions)
- [ ] semantic_similarity.yaml (0/6 questions)
- [ ] table_data.yaml (0/4 questions)
- [ ] formulas.yaml (0/4 questions)
- [ ] multi_hop_reasoning.yaml (0/5 questions)
- [ ] code_understanding.yaml (0/4 questions)
- [ ] acronyms.yaml (0/3 questions)
- [ ] contextual.yaml (0/4 questions)
- [ ] negation.yaml (0/3 questions)
- [ ] temporal.yaml (0/3 questions)
- [ ] factual.yaml (0/4 questions)
- [ ] conceptual.yaml (0/5 questions)

**Total Progress: 0/50 questions created**

## Next Steps

1. Review corpus documents to understand content
2. Create questions following the template
3. Have domain expert review questions
4. Validate questions with initial test runs
5. Iterate based on feedback
