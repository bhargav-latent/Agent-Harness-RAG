# Evaluation Framework Methodology

> **Comprehensive methodology for comparing FileSearch vs Vector Store RAG performance**

## Framework Philosophy

### Core Principles

1. **Fairness** - Both methods evaluated under identical conditions
2. **Comprehensiveness** - Cover diverse query types and use cases
3. **Realism** - Questions reflect actual user needs
4. **Reproducibility** - Clear methodology for consistent results
5. **Actionability** - Results inform deployment decisions

### Evaluation Goals

- **Identify strengths and weaknesses** of each retrieval method
- **Quantify performance differences** across categories
- **Guide hybrid strategy design** combining both approaches
- **Inform infrastructure decisions** based on use cases
- **Establish baseline metrics** for future improvements

---

## Methodology Overview

### Three-Phase Approach

#### **Phase 1: Test Design**
- Define evaluation categories (12 categories)
- Create diverse test questions (50 total)
- Establish ground truth answers
- Identify expected source documents
- Assign difficulty ratings

#### **Phase 2: Execution**
- Run FileSearch agent on all questions
- Run Vector Store agent on all questions
- Record responses and metadata
- Measure performance characteristics
- Collect retrieval diagnostics

#### **Phase 3: Analysis**
- Score responses using rubrics
- Calculate aggregate metrics
- Perform category-level analysis
- Generate comparison reports
- Identify patterns and insights

---

## Test Design Methodology

### Question Selection Criteria

#### 1. **Diversity Across Categories**
- Balanced distribution across 12 categories
- Each category tests specific capabilities
- Coverage of both method's strengths and weaknesses

#### 2. **Difficulty Distribution**
```
Level 1 (Easy):      10 questions - Basic factual lookup
Level 2 (Medium):    15 questions - Moderate complexity
Level 3 (Moderate):  15 questions - Multi-step reasoning
Level 4 (Hard):       7 questions - Complex synthesis
Level 5 (Expert):     3 questions - Deep understanding
```

#### 3. **Query Pattern Variation**
- Direct questions: "What is X?"
- Procedural: "How to do X?"
- Comparative: "Compare X and Y"
- Conceptual: "Why does X work?"
- Troubleshooting: "How to fix X?"

#### 4. **Length Variation**
- Short queries: 3-8 words
- Medium queries: 8-15 words
- Long queries: 15+ words
- Natural language variations

### Ground Truth Establishment

#### Requirements for Each Question

**1. Expected Answer**
- Clear, factual correct response
- Sufficient detail for comparison
- Citable from source documents
- Unambiguous interpretation

**2. Source Documents**
- List all documents containing answer
- Specify sections/pages if applicable
- Include both direct and supporting sources
- Note if answer spans multiple documents

**3. Evaluation Criteria**
- Key facts that must be present
- Acceptable variations in wording
- Minimum completeness threshold
- Citation requirements

**4. Difficulty Justification**
- Why this difficulty rating?
- What makes it easy/hard?
- Required reasoning steps
- Document complexity involved

### Document Corpus Preparation

#### Current Corpus
```
documents/
├── The Essence of Software Engineering.pdf
├── attention_is_all_you_need.pdf
├── thinkpython2.pdf
└── CLAUDE.md (Deep Agents documentation)
```

#### Corpus Requirements
- **Consistency** - Same documents for both methods
- **Indexing** - Proper preprocessing and chunking
- **Metadata** - Track source attribution
- **Versioning** - Fixed corpus per evaluation run

#### Preprocessing Steps
1. **Extract text** from PDFs
2. **Chunk documents** (512 tokens recommended)
3. **Create embeddings** for vector store
4. **Build search indices** for file search
5. **Preserve structure** (tables, formulas, code)

---

## Execution Methodology

### Agent Configuration

#### FileSearch Agent Setup
- **Tools:** grep, glob, read_file, ls
- **Strategy:** Keyword-based retrieval
- **Parameters:**
  - Case sensitivity: configurable
  - Context lines: 3 before/after
  - Max results: 20 documents
  - Ranking: TF-IDF or BM25

#### Vector Store Agent Setup
- **Tools:** vector_search, read_file
- **Strategy:** Semantic similarity
- **Parameters:**
  - Embedding model: text-embedding-3-small
  - Similarity metric: cosine
  - Top-k: 5-10 documents
  - Reranking: optional cross-encoder

### Fair Comparison Protocol

#### Control Variables
1. **Same LLM** for both agents (e.g., GPT-4)
2. **Same document corpus** and versions
3. **Same question set** in same order
4. **Same temperature** (0.0 for consistency)
5. **Same context limits** for generation

#### Measured Variables
1. **Answer quality** (correctness, completeness)
2. **Retrieval quality** (relevant docs retrieved)
3. **Response time** (end-to-end latency)
4. **Token usage** (cost estimation)
5. **Failure modes** (when/why it fails)

### Data Collection

#### Per-Question Recording

**Input Data:**
- Question ID
- Question text
- Category
- Difficulty level
- Expected answer
- Expected sources

**Agent Response:**
- Generated answer
- Retrieved documents (IDs)
- Retrieved document snippets
- Response timestamp
- Response time (seconds)
- Token count (input + output)

**Retrieval Diagnostics:**
- Number of documents retrieved
- Relevance scores per document
- Ranking order
- Search queries used (if multiple)
- Tool calls made

### Multiple Run Protocol

#### Why Multiple Runs?
- Account for LLM non-determinism
- Measure consistency/stability
- Identify edge cases
- Calculate confidence intervals

#### Recommended Approach
- **Minimum:** 3 runs per question
- **Temperature:** 0.0 for main runs
- **Temperature:** 0.3 for variation analysis
- **Aggregation:** Median scores, average times

---

## Scoring Methodology

### Evaluation Approach Options

#### Option 1: Manual Human Evaluation
**Process:**
- Domain expert reviews each answer
- Scores using detailed rubric
- Records reasoning for scores
- Time-intensive but highly accurate

**Best for:**
- Initial baseline establishment
- Disputed/complex cases
- Validation of automated scoring

#### Option 2: LLM-as-Judge
**Process:**
- Use strong LLM (GPT-4, Claude) to evaluate
- Provide ground truth and scoring rubric
- Generate scores with explanations
- Faster and consistent

**Best for:**
- Large-scale evaluation
- Consistent application of rubrics
- Initial screening before human review

#### Option 3: Hybrid (Recommended)
**Process:**
1. LLM evaluates all answers
2. Human reviews low-confidence cases
3. Human spot-checks random sample (10%)
4. Human has final authority on disputes

**Best for:**
- Balanced speed and accuracy
- Scalability with quality control
- Resource-constrained environments

### Scoring Rubrics

#### Four Core Dimensions (0-5 each)

**1. Correctness**
- 5: Completely accurate, no errors
- 4: Accurate with minor imprecision
- 3: Mostly accurate, some errors
- 2: Partially accurate, significant errors
- 1: Mostly inaccurate
- 0: Completely wrong or no answer

**2. Completeness**
- 5: Covers all aspects thoroughly
- 4: Covers main points, minor gaps
- 3: Covers key points, missing details
- 2: Incomplete, missing major aspects
- 1: Severely incomplete
- 0: No answer or totally insufficient

**3. Relevance**
- 5: Directly addresses question perfectly
- 4: Addresses question, minor tangents
- 3: Mostly relevant, some off-topic
- 2: Partially relevant
- 1: Barely relevant
- 0: Irrelevant or no answer

**4. Citation Quality**
- 5: Perfect source attribution
- 4: Good citations, minor gaps
- 3: Some citations, incomplete
- 2: Weak or vague citations
- 1: No proper citations
- 0: No citations at all

#### Additional Measurements

**Performance Metrics:**
- Response time (seconds)
- Token usage (input + output)
- Number of documents retrieved
- Number of relevant documents retrieved

**Retrieval Metrics:**
- Precision@K: Relevant retrieved / Total retrieved
- Recall@K: Relevant retrieved / Total relevant
- MRR: Mean reciprocal rank of first relevant doc
- NDCG: Normalized discounted cumulative gain

---

## Analysis Methodology

### Individual Question Analysis

For each question, compare:
- **Winner** - Which method scored higher?
- **Score Gap** - Magnitude of difference
- **Failure Modes** - Why did one fail?
- **Retrieval Success** - Did it find right docs?
- **Efficiency** - Time and token costs

### Category-Level Analysis

For each category:
- **Average Scores** - Mean across questions
- **Win Rate** - Percentage each method wins
- **Performance Patterns** - Consistent strengths?
- **Difficulty Correlation** - Harder → worse?
- **Retrieval Effectiveness** - Finding right docs?

### Aggregate Analysis

#### Overall Performance
- **Total Score** - Sum across all questions
- **Mean Score** - Average performance
- **Median Score** - Middle performance
- **Standard Deviation** - Consistency
- **Win Rate** - Head-to-head comparison

#### Performance Characteristics
- **Best Categories** - Where each excels
- **Worst Categories** - Where each struggles
- **Efficiency Profile** - Speed vs accuracy tradeoff
- **Cost Profile** - Token usage patterns
- **Failure Analysis** - Common failure modes

### Statistical Significance

#### Tests to Run
- **T-test** - Mean score difference significant?
- **Wilcoxon** - Non-parametric comparison
- **Chi-square** - Win rate distribution
- **Cohen's d** - Effect size measurement

#### Confidence Intervals
- Report 95% confidence intervals
- Acknowledge uncertainty
- Avoid overstating differences
- Note sample size limitations

---

## Reporting Methodology

### Report Structure

#### Executive Summary
- Key findings (2-3 bullets)
- Overall winner (if any)
- Recommended strategy
- Cost-benefit analysis

#### Detailed Results
- Category-by-category breakdown
- Individual question analysis
- Performance characteristics
- Failure mode analysis

#### Visualizations
- Score distribution charts
- Category comparison radar plots
- Win rate by category bar charts
- Response time box plots
- Cost analysis graphs

#### Recommendations
- When to use FileSearch
- When to use Vector Store
- Hybrid strategy suggestions
- Implementation guidance

### Interpretation Guidelines

#### No Single Winner Expected
- Each method has strengths
- Context matters greatly
- Hybrid often best
- Cost-accuracy tradeoffs

#### Category Insights
- FileSearch: Exact match, structured data
- Vector Store: Semantic, conceptual
- Both: Code, factual lookup
- Neither perfect for all cases

#### Deployment Implications
- Infrastructure requirements
- Maintenance considerations
- Scaling characteristics
- Cost projections

---

## Validation and Quality Control

### Question Quality Checks

Before evaluation:
- [ ] Ground truth verified by expert
- [ ] Expected sources identified
- [ ] Category assignment justified
- [ ] Difficulty rating appropriate
- [ ] No ambiguous wording
- [ ] Answerable from corpus

### Evaluation Quality Checks

During evaluation:
- [ ] Same corpus version used
- [ ] Fair configuration for both
- [ ] Multiple runs completed
- [ ] Timestamps recorded
- [ ] All data captured
- [ ] No manual intervention

### Analysis Quality Checks

After evaluation:
- [ ] Scoring rubric applied consistently
- [ ] Statistical tests valid
- [ ] Confidence intervals reported
- [ ] Limitations acknowledged
- [ ] Recommendations justified
- [ ] Reproducible methodology

---

## Iteration and Improvement

### Framework Evolution

#### Version 1.0 (Initial)
- 12 categories, 50 questions
- Basic scoring rubrics
- Manual + LLM evaluation
- Standard metrics

#### Future Enhancements
- Expand question set (100+)
- Add new categories as needed
- Refine scoring rubrics
- Automated evaluation pipeline
- Real user query analysis
- A/B testing framework

### Continuous Improvement

**Question Set Refinement:**
- Add questions that expose differences
- Remove redundant questions
- Update based on real usage patterns
- Incorporate edge cases discovered

**Methodology Refinement:**
- Improve scoring consistency
- Optimize evaluation efficiency
- Enhance statistical rigor
- Better visualization tools

---

## Best Practices

### Do's ✅

- Use same corpus and configuration
- Run multiple times for stability
- Document all parameters and settings
- Include confidence intervals
- Acknowledge limitations
- Focus on actionable insights

### Don'ts ❌

- Don't cherry-pick favorable results
- Don't ignore failure modes
- Don't overstate small differences
- Don't skip ground truth validation
- Don't forget cost considerations
- Don't claim universal superiority

---

## Appendix: Evaluation Checklist

### Pre-Evaluation
- [ ] Test questions created and validated
- [ ] Ground truth established
- [ ] Document corpus prepared
- [ ] Both agents configured
- [ ] Fair comparison parameters set
- [ ] Data collection system ready

### During Evaluation
- [ ] Running both methods on same questions
- [ ] Recording all required metrics
- [ ] Monitoring for issues
- [ ] Multiple runs completed
- [ ] Data backup in place

### Post-Evaluation
- [ ] All responses scored
- [ ] Aggregate metrics calculated
- [ ] Category analysis completed
- [ ] Statistical tests performed
- [ ] Report generated
- [ ] Recommendations documented
- [ ] Results archived

---

**Next Steps:** See [categories.md](categories.md) for detailed category definitions and [metrics.md](metrics.md) for complete scoring specifications.
