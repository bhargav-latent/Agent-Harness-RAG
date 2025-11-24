# Evaluation Results Directory

This directory stores the results from evaluation runs.

## Structure

```
results/
├── run_YYYYMMDD_HHMMSS/          # Timestamped run folder
│   ├── config.yaml                # Run configuration
│   ├── filesearch_results.json    # FileSearch agent results
│   ├── vectorstore_results.json   # Vector Store agent results
│   ├── comparison.json            # Side-by-side comparison
│   ├── metrics.json               # Aggregate metrics
│   ├── report.html                # Visual comparison report
│   └── analysis.md                # Detailed analysis notes
├── latest -> run_YYYYMMDD_HHMMSS/ # Symlink to most recent run
└── baseline/                      # Initial baseline results
    └── ...
```

## Result Files

### config.yaml
Records the configuration for reproducibility:
```yaml
run_id: "run_20251124_093000"
date: "2025-11-24"
corpus_version: "v1.0"
questions_version: "v1.0"
filesearch_config:
  agent_id: "filesearch_v1"
  model: "gpt-4"
  tools: ["grep", "glob", "read_file"]
  parameters:
    temperature: 0.0
    max_tokens: 2000
vectorstore_config:
  agent_id: "vectorstore_v1"
  model: "gpt-4"
  embedding_model: "text-embedding-3-small"
  tools: ["vector_search", "read_file"]
  parameters:
    temperature: 0.0
    max_tokens: 2000
    top_k: 5
```

### filesearch_results.json / vectorstore_results.json
Individual results per question:
```json
{
  "run_id": "run_20251124_093000",
  "method": "filesearch",
  "results": [
    {
      "question_id": "Q001",
      "question_text": "...",
      "generated_answer": "...",
      "retrieved_docs": [...],
      "scores": {
        "correctness": 5,
        "completeness": 4,
        "relevance": 5,
        "citation": 3,
        "total": 4.25
      },
      "performance": {
        "response_time_seconds": 2.1,
        "tokens_input": 450,
        "tokens_output": 406,
        "tokens_total": 856
      },
      "retrieval": {
        "docs_retrieved": 2,
        "docs_relevant": 2,
        "precision": 1.0
      }
    }
  ]
}
```

### comparison.json
Side-by-side comparison:
```json
{
  "run_id": "run_20251124_093000",
  "comparisons": [
    {
      "question_id": "Q001",
      "filesearch": {
        "score": 4.25,
        "time": 2.1
      },
      "vectorstore": {
        "score": 4.0,
        "time": 3.8
      },
      "winner": "filesearch",
      "score_diff": 0.25
    }
  ]
}
```

### metrics.json
Aggregate metrics:
```json
{
  "run_id": "run_20251124_093000",
  "overall": {
    "filesearch": {
      "mean_score": 3.8,
      "median_score": 4.0,
      "std_dev": 0.8,
      "win_rate": 0.42,
      "avg_response_time": 3.2,
      "avg_token_cost": 0.05
    },
    "vectorstore": {
      "mean_score": 4.1,
      "median_score": 4.2,
      "std_dev": 0.7,
      "win_rate": 0.56,
      "avg_response_time": 4.8,
      "avg_token_cost": 0.08
    }
  },
  "by_category": {...},
  "statistical_tests": {
    "t_test_pvalue": 0.023,
    "cohens_d": 0.42
  }
}
```

### report.html
Interactive HTML dashboard with:
- Executive summary
- Overall metrics comparison
- Category-by-category breakdown
- Individual question results
- Performance charts
- Failure analysis

### analysis.md
Detailed written analysis:
- Key findings
- Unexpected results
- Failure mode patterns
- Recommendations
- Next steps

## Viewing Results

### Latest Results
```bash
# View in browser
open evaluation/results/latest/report.html

# View metrics
cat evaluation/results/latest/metrics.json | jq

# Read analysis
cat evaluation/results/latest/analysis.md
```

### Compare Runs
```bash
# Compare two runs
python evaluation/scripts/compare_runs.py run_20251124 run_20251125
```

## Result Versioning

- Each run is timestamped
- Results are immutable once created
- Configuration captured for reproducibility
- Historical runs preserved for trend analysis

## Archiving

Old results can be archived:
```bash
# Archive runs older than 30 days
python evaluation/scripts/archive_old_results.py --days 30
```

Archived results moved to `results/archive/` with compression.

## Best Practices

1. **Never manually edit results** - Regenerate if needed
2. **Keep configuration with results** - For reproducibility
3. **Document unusual runs** - Add notes to analysis.md
4. **Compare to baseline** - Track improvements over time
5. **Archive regularly** - Keep directory manageable

## Status

Currently: No evaluation runs yet

To perform first evaluation:
1. Create test questions in `evaluation/questions/`
2. Set up FileSearch and Vector Store agents
3. Run evaluation script
4. Results will be generated here automatically
