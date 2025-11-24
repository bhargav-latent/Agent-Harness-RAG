# Evaluation Scripts Directory

This directory will contain helper scripts for running evaluations and generating reports.

## Planned Scripts

### Core Evaluation Scripts

#### `run_evaluation.py`
**Purpose:** Execute full evaluation comparing FileSearch vs Vector Store

**Usage:**
```bash
python evaluation/scripts/run_evaluation.py \
  --questions evaluation/questions/ \
  --output evaluation/results/run_$(date +%Y%m%d_%H%M%S) \
  --config evaluation/config.yaml
```

**Features:**
- Load all test questions
- Initialize both agents (FileSearch and Vector Store)
- Run questions through both agents
- Collect responses and metrics
- Save results in structured format

---

#### `generate_report.py`
**Purpose:** Generate HTML comparison report from results

**Usage:**
```bash
python evaluation/scripts/generate_report.py \
  --results evaluation/results/latest/ \
  --output evaluation/results/latest/report.html
```

**Features:**
- Load results JSON files
- Calculate aggregate metrics
- Create visualizations (charts, graphs)
- Generate interactive HTML dashboard
- Include detailed breakdowns

---

#### `llm_judge.py`
**Purpose:** Use LLM to evaluate answer quality automatically

**Usage:**
```bash
python evaluation/scripts/llm_judge.py \
  --results evaluation/results/latest/filesearch_results.json \
  --questions evaluation/questions/ \
  --model gpt-4 \
  --output evaluation/results/latest/filesearch_scored.json
```

**Features:**
- Load questions with ground truth
- Load generated answers
- Use LLM to score on four dimensions
- Generate explanations for scores
- Save scored results

---

### Analysis Scripts

#### `compare_runs.py`
**Purpose:** Compare results from different evaluation runs

**Usage:**
```bash
python evaluation/scripts/compare_runs.py \
  --run1 evaluation/results/run_20251124_093000 \
  --run2 evaluation/results/run_20251125_103000 \
  --output comparison_report.html
```

**Features:**
- Load both run results
- Calculate deltas in metrics
- Identify improvements/regressions
- Generate comparison report

---

#### `analyze_failures.py`
**Purpose:** Deep dive into failure modes and patterns

**Usage:**
```bash
python evaluation/scripts/analyze_failures.py \
  --results evaluation/results/latest/ \
  --threshold 3.0 \
  --output failure_analysis.md
```

**Features:**
- Identify low-scoring questions
- Categorize failure types
- Find patterns (category, difficulty, etc.)
- Generate detailed failure analysis

---

#### `statistical_analysis.py`
**Purpose:** Perform statistical tests on results

**Usage:**
```bash
python evaluation/scripts/statistical_analysis.py \
  --results evaluation/results/latest/ \
  --output stats_report.md
```

**Features:**
- T-tests for mean comparison
- Wilcoxon signed-rank test
- Cohen's d effect size
- Confidence intervals
- Statistical significance testing

---

### Utility Scripts

#### `validate_questions.py`
**Purpose:** Validate question format and completeness

**Usage:**
```bash
python evaluation/scripts/validate_questions.py \
  --questions evaluation/questions/ \
  --corpus documents/
```

**Features:**
- Check YAML format
- Verify all required fields present
- Validate source documents exist
- Check for duplicate IDs
- Verify ground truth answerability

---

#### `prepare_corpus.py`
**Purpose:** Prepare document corpus for evaluation

**Usage:**
```bash
python evaluation/scripts/prepare_corpus.py \
  --input documents/ \
  --output data/processed_corpus/ \
  --chunk-size 512 \
  --chunk-overlap 50
```

**Features:**
- Extract text from PDFs
- Chunk documents appropriately
- Generate embeddings for vector store
- Create search indices for file search
- Save preprocessed corpus

---

#### `archive_results.py`
**Purpose:** Archive old evaluation results

**Usage:**
```bash
python evaluation/scripts/archive_results.py \
  --results evaluation/results/ \
  --days 30 \
  --archive evaluation/results/archive/
```

**Features:**
- Find results older than threshold
- Compress and archive
- Maintain index of archived runs
- Clean up results directory

---

## Script Development Priorities

### Phase 1: Core Functionality
1. ✅ Framework documentation complete
2. ⏳ Question creation in progress
3. 📝 `run_evaluation.py` - High priority
4. 📝 `llm_judge.py` - High priority
5. 📝 `generate_report.py` - High priority

### Phase 2: Analysis Tools
6. 📝 `analyze_failures.py` - Medium priority
7. 📝 `statistical_analysis.py` - Medium priority
8. 📝 `compare_runs.py` - Medium priority

### Phase 3: Utilities
9. 📝 `validate_questions.py` - Low priority
10. 📝 `prepare_corpus.py` - Low priority
11. 📝 `archive_results.py` - Low priority

## Implementation Notes

### Dependencies
Scripts will likely require:
```
langchain
openai
numpy
pandas
scipy
pyyaml
jinja2
plotly
```

### Configuration
Shared configuration in `evaluation/config.yaml`:
```yaml
# API keys and endpoints
openai_api_key: ${OPENAI_API_KEY}
embedding_model: "text-embedding-3-small"

# Evaluation settings
temperature: 0.0
max_tokens: 2000
top_k: 5

# Scoring
llm_judge_model: "gpt-4"
human_review_threshold: 0.3  # Auto-score if confidence > 0.7

# Paths
corpus_path: "documents/"
questions_path: "evaluation/questions/"
results_path: "evaluation/results/"
```

### Common Utilities
Create `evaluation/scripts/utils.py` with shared functions:
- Load questions from YAML
- Load results from JSON
- Calculate metrics
- Generate charts
- Format reports

## Usage Patterns

### Full Evaluation Workflow
```bash
# 1. Validate questions
python evaluation/scripts/validate_questions.py

# 2. Prepare corpus (if needed)
python evaluation/scripts/prepare_corpus.py

# 3. Run evaluation
RUN_ID=$(date +%Y%m%d_%H%M%S)
python evaluation/scripts/run_evaluation.py \
  --output evaluation/results/run_$RUN_ID

# 4. Score with LLM judge
python evaluation/scripts/llm_judge.py \
  --results evaluation/results/run_$RUN_ID

# 5. Generate report
python evaluation/scripts/generate_report.py \
  --results evaluation/results/run_$RUN_ID

# 6. View report
open evaluation/results/run_$RUN_ID/report.html
```

### Continuous Evaluation
```bash
# Run nightly and compare to baseline
python evaluation/scripts/run_evaluation.py --output results/nightly_$(date +%Y%m%d)
python evaluation/scripts/compare_runs.py \
  --run1 results/baseline \
  --run2 results/nightly_$(date +%Y%m%d)
```

## Testing Scripts

Each script should have tests:
```
evaluation/scripts/tests/
├── test_run_evaluation.py
├── test_llm_judge.py
├── test_generate_report.py
└── ...
```

Run tests:
```bash
pytest evaluation/scripts/tests/
```

## Documentation

Each script should include:
- Docstring explaining purpose
- Usage examples
- Parameter descriptions
- Expected input/output formats
- Error handling notes

## Contributing

When adding new scripts:
1. Follow existing naming conventions
2. Add entry to this README
3. Include comprehensive docstrings
4. Add tests if applicable
5. Update dependencies if needed

## Status

Currently: Framework documentation complete, scripts pending implementation

Next steps:
1. Finish question creation
2. Implement `run_evaluation.py`
3. Implement `llm_judge.py`
4. Implement `generate_report.py`
5. Test with initial question set
