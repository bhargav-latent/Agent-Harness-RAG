# Evaluation Metrics & Scoring Rubrics

> **Comprehensive metrics and scoring guidelines for RAG evaluation**

## Metrics Overview

Evaluation uses three levels of metrics:
1. **Per-Question Metrics** - Individual answer quality
2. **Per-Category Metrics** - Category-level aggregation
3. **Overall Metrics** - System-wide performance

---

## Part 1: Per-Question Scoring

### Four Core Dimensions (0-5 Scale)

Each answer is scored on four dimensions. Scores are integers from 0-5.

---

#### **Dimension 1: Correctness**

**Definition:** Factual accuracy of the information provided

**Scoring Rubric:**

| Score | Criteria | Description |
|-------|----------|-------------|
| **5** | Perfect | All facts correct, no errors or inaccuracies |
| **4** | Excellent | Correct with minor imprecision (e.g., rounding, slight wording variance) |
| **3** | Good | Mostly accurate but contains minor factual errors or omissions |
| **2** | Fair | Partially accurate with significant errors or misleading information |
| **1** | Poor | Mostly inaccurate, more wrong than right |
| **0** | Failed | Completely wrong, irrelevant, or no answer provided |

**Examples:**

```
Question: "What is the token limit for GPT-4?"

Score 5: "GPT-4 has a 8,192 token limit for the base model and 32,768 for GPT-4-32k"
Score 4: "GPT-4 has approximately 8,000 tokens" (minor imprecision)
Score 3: "GPT-4 has 8,192 tokens" (missing 32k variant)
Score 2: "GPT-4 has 4,096 tokens" (wrong number)
Score 1: "GPT-4 has unlimited tokens" (completely wrong)
Score 0: "I don't know" or irrelevant answer
```

**Evaluation Guidelines:**
- Verify each factual claim against ground truth
- Minor rounding acceptable if clearly stated
- Omissions hurt score but less than errors
- No credit for "partially right" on yes/no questions

---

#### **Dimension 2: Completeness**

**Definition:** Coverage of all relevant aspects of the answer

**Scoring Rubric:**

| Score | Criteria | Description |
|-------|----------|-------------|
| **5** | Comprehensive | Covers all key points and important details thoroughly |
| **4** | Complete | Covers all main points but missing minor supporting details |
| **3** | Adequate | Covers key points but missing some important details |
| **2** | Incomplete | Missing major aspects or key components |
| **1** | Minimal | Barely scratches the surface, most content missing |
| **0** | None | No meaningful content or no answer |

**Examples:**

```
Question: "Explain the three types of middleware in Deep Agents"

Score 5: Explains TodoList, Filesystem, SubAgent with purposes and tools
Score 4: Explains all three but missing some tool details
Score 3: Explains two middleware types thoroughly, one briefly
Score 2: Only explains one middleware type
Score 1: Mentions middleware exists but no explanation
Score 0: No answer or completely off-topic
```

**Evaluation Guidelines:**
- List all expected components in ground truth
- Major components > minor details
- Depth matters (explain not just list)
- Penalize significant omissions more heavily

**Expected Component Checklist:**
- [ ] Main concept explained
- [ ] Key components identified
- [ ] Important details provided
- [ ] Context/purpose included
- [ ] Examples given (if applicable)

---

#### **Dimension 3: Relevance**

**Definition:** How directly the answer addresses the question asked

**Scoring Rubric:**

| Score | Criteria | Description |
|-------|----------|-------------|
| **5** | Perfect | Directly and precisely answers the exact question asked |
| **4** | Excellent | Answers the question with minor tangential content |
| **3** | Good | Mostly relevant but includes some off-topic information |
| **2** | Fair | Partially relevant, significant off-topic content |
| **1** | Poor | Barely relevant, mostly off-topic |
| **0** | Irrelevant | Completely unrelated to the question |

**Examples:**

```
Question: "How does StateBackend differ from StoreBackend?"

Score 5: Compares the two backends directly on key dimensions
Score 4: Compares both but includes extra info about FilesystemBackend
Score 3: Explains StoreBackend well but only mentions StateBackend briefly
Score 2: Explains general backend concepts without comparing
Score 1: Discusses middleware instead of backends
Score 0: Talks about something completely different
```

**Evaluation Guidelines:**
- Focus on question type (what, how, why, compare)
- Direct answers > tangential information
- Related but not requested info acceptable if brief
- Penalize answers that ignore question structure

**Question Type Expectations:**
- **What:** Definition and explanation
- **How:** Process, mechanism, steps
- **Why:** Rationale, reasoning, motivation
- **Compare:** Similarities and differences
- **List:** Enumeration with brief descriptions

---

#### **Dimension 4: Citation Quality**

**Definition:** Quality and accuracy of source attribution

**Scoring Rubric:**

| Score | Criteria | Description |
|-------|----------|-------------|
| **5** | Excellent | All claims cited with accurate sources, specific locations |
| **4** | Good | Most claims cited, minor gaps or imprecise locations |
| **3** | Adequate | Some citations but incomplete or vague |
| **2** | Weak | Few citations or very vague attribution |
| **1** | Poor | No proper citations but vague mention of sources |
| **0** | None | No citations or source attribution at all |

**Examples:**

```
Score 5: "According to CLAUDE.md section 'Backend Storage', StateBackend stores files in LangGraph state (line 234)"

Score 4: "CLAUDE.md states that StateBackend is ephemeral storage"

Score 3: "The documentation mentions StateBackend is temporary"

Score 2: "I found that StateBackend is for temporary files"

Score 1: "StateBackend is for temporary use"

Score 0: Claims without any source mention
```

**Evaluation Guidelines:**
- Document name minimum requirement
- Section/page/line is better
- Direct quotes deserve highest score
- "The documentation says..." acceptable
- No citation = score 0

**Citation Levels:**
1. **Specific:** File + section + line/page
2. **Moderate:** File + section
3. **Basic:** File only
4. **Vague:** "The documentation..."
5. **None:** No attribution

---

### Composite Score Calculation

**Total Score per Question:**
```
Total Score = (Correctness + Completeness + Relevance + Citation Quality) / 4
Range: 0.0 to 5.0
```

**Weighted Score (Optional):**
```
Weighted Score = (Correctness × 0.4) + (Completeness × 0.3) +
                 (Relevance × 0.2) + (Citation × 0.1)

Rationale: Correctness most important, then completeness
```

**Pass/Fail Threshold:**
- **Pass:** Total Score ≥ 3.0 (60%)
- **Good:** Total Score ≥ 4.0 (80%)
- **Excellent:** Total Score ≥ 4.5 (90%)

---

## Part 2: Performance Metrics

### Response Time

**Measurement:**
```
Response Time = End Timestamp - Start Timestamp
Unit: Seconds
Precision: 0.01s (10ms)
```

**Interpretation:**
- **Fast:** < 2 seconds
- **Acceptable:** 2-5 seconds
- **Slow:** 5-10 seconds
- **Very Slow:** > 10 seconds

**Percentiles to Report:**
- P50 (Median)
- P95 (95th percentile)
- P99 (99th percentile)
- Max

---

### Token Usage

**Measurement:**
```
Total Tokens = Input Tokens + Output Tokens
Cost Estimate = (Input Tokens × Input Price) + (Output Tokens × Output Price)
```

**Interpretation:**
- Efficiency: Tokens per question
- Cost: Estimated $ per question
- Compare: FileSearch vs Vector Store

**Typical Ranges:**
- **Short answer:** 500-2000 tokens
- **Medium answer:** 2000-5000 tokens
- **Long answer:** 5000-10000 tokens

---

### Retrieved Documents

**Metrics:**
```
Document Count = Number of documents retrieved
Relevant Count = Number of relevant documents (human/LLM judged)
Irrelevant Count = Document Count - Relevant Count
```

**Calculations:**
```
Retrieval Precision = Relevant Count / Document Count
Retrieval Recall = Relevant Count / Total Relevant in Corpus
```

**Interpretation:**
- **High Precision:** Few irrelevant docs (> 0.8)
- **High Recall:** Found most relevant docs (> 0.8)
- **Balanced:** Both > 0.7

---

### Retrieval Quality Metrics

#### Precision@K
```
Precision@K = (Number of relevant docs in top K) / K

Example: If 4 out of top 5 docs are relevant
Precision@5 = 4 / 5 = 0.80
```

#### Recall@K
```
Recall@K = (Number of relevant docs in top K) / (Total relevant docs in corpus)

Example: If 4 out of 6 total relevant docs are in top 5
Recall@5 = 4 / 6 = 0.67
```

#### Mean Reciprocal Rank (MRR)
```
MRR = 1 / (Rank of first relevant document)

Example: First relevant doc at position 3
MRR = 1 / 3 = 0.33
```

#### Normalized Discounted Cumulative Gain (NDCG)
```
DCG@K = Σ (relevance_i / log2(i + 1)) for i = 1 to K
NDCG@K = DCG@K / IDCG@K

Where IDCG = ideal DCG (perfect ranking)
```

**Interpretation:**
- NDCG = 1.0: Perfect ranking
- NDCG > 0.8: Excellent
- NDCG > 0.6: Good
- NDCG < 0.4: Poor

---

## Part 3: Aggregate Metrics

### Overall Performance

**Mean Score (Primary Metric):**
```
Mean Score = Σ(Total Score per Question) / Number of Questions
Range: 0.0 to 5.0
```

**Median Score:**
```
Median = Middle value when all scores sorted
More robust to outliers than mean
```

**Standard Deviation:**
```
StdDev = Measure of score consistency
Low StdDev = Consistent performance
High StdDev = Variable performance
```

---

### Category-Level Metrics

**Per Category:**
```
Category Mean = Average score across questions in category
Category Win Rate = (Questions won in category) / (Total in category)
```

**Category Comparison Table:**

| Category | FileSearch Mean | Vector Mean | Winner | Gap |
|----------|----------------|-------------|--------|-----|
| Exact Match | 4.5 | 3.2 | FileSearch | +1.3 |
| Semantic | 2.8 | 4.6 | VectorStore | +1.8 |
| ... | ... | ... | ... | ... |

---

### Win Rate Analysis

**Head-to-Head Comparison:**
```
Win = Method with higher score
Tie = Scores within 0.2 points
Loss = Method with lower score

Win Rate = Wins / Total Questions
```

**Statistical Significance:**
```
Use binomial test:
H0: Both methods equally likely to win (p = 0.5)
H1: One method more likely to win (p ≠ 0.5)

Significant if p-value < 0.05
```

---

### Statistical Tests

#### T-Test (Mean Comparison)
```
Purpose: Test if mean scores significantly different
Conditions: Normal distribution, continuous scores
Interpretation: p < 0.05 = statistically significant difference
```

#### Wilcoxon Signed-Rank Test
```
Purpose: Non-parametric alternative to t-test
Conditions: Paired samples, ordinal data
Use when: Scores not normally distributed
```

#### Cohen's d (Effect Size)
```
Cohen's d = (Mean1 - Mean2) / Pooled StdDev

Interpretation:
- Small: d = 0.2
- Medium: d = 0.5
- Large: d = 0.8
```

---

## Part 4: Efficiency Metrics

### Speed-Accuracy Tradeoff

**Efficiency Score:**
```
Efficiency = Accuracy Score / Response Time

Higher = Better (more accurate per second)
```

**Cost-Accuracy Tradeoff:**
```
Cost Efficiency = Accuracy Score / Token Cost

Higher = Better (more accurate per dollar)
```

---

### Scalability Metrics

**Throughput:**
```
Throughput = Questions Answered / Hour
```

**Latency Distribution:**
```
Report P50, P95, P99, Max
Identify outliers and investigate
```

---

## Part 5: Qualitative Metrics

### Failure Mode Analysis

**Categorize Failures:**
1. **Retrieval Failure:** Couldn't find relevant docs
2. **Generation Failure:** Found docs but wrong answer
3. **Citation Failure:** Right answer but no source
4. **Understanding Failure:** Misunderstood question
5. **Format Failure:** Correct info, wrong format

**For Each Failure:**
- Count frequency
- Identify patterns
- Correlate with categories
- Propose improvements

---

### Confidence Scoring

**LLM-Generated Confidence:**
```
Ask LLM to rate confidence: 1-5
1 = Very uncertain
5 = Very confident

Analyze correlation with correctness
```

---

## Part 6: Reporting Format

### Summary Metrics Table

```
| Metric | FileSearch | VectorStore | Difference |
|--------|-----------|-------------|------------|
| Mean Score | 3.8 | 4.1 | +0.3 (VectorStore) |
| Median Score | 4.0 | 4.2 | +0.2 |
| Win Rate | 42% | 56% | +14% (VectorStore) |
| Avg Response Time | 3.2s | 4.8s | +1.6s (FileSearch faster) |
| Avg Token Cost | $0.05 | $0.08 | +$0.03 (FileSearch cheaper) |
| Precision@5 | 0.82 | 0.76 | +0.06 (FileSearch) |
| Recall@5 | 0.68 | 0.84 | +0.16 (VectorStore) |
```

---

### Category Breakdown Table

```
| Category | FileSearch | VectorStore | Winner |
|----------|------------|-------------|--------|
| Exact Match | 4.5 ⭐ | 3.2 | FileSearch |
| Semantic | 2.8 | 4.6 ⭐ | VectorStore |
| Tables | 4.2 ⭐ | 3.5 | FileSearch |
| Formulas | 4.0 ⭐ | 3.3 | FileSearch |
| Multi-hop | 2.5 | 4.3 ⭐ | VectorStore |
| Code | 3.8 | 4.0 ⭐ | VectorStore |
| Acronyms | 2.6 | 4.1 ⭐ | VectorStore |
| Contextual | 2.9 | 4.2 ⭐ | VectorStore |
| Negation | 3.4 | 3.5 ⭐ | VectorStore |
| Temporal | 3.6 | 3.4 | FileSearch |
| Factual | 4.3 ⭐ | 3.8 | FileSearch |
| Conceptual | 2.7 | 4.5 ⭐ | VectorStore |
```

---

### Detailed Question Results

```
Question ID: Q001
Category: Exact Match
Difficulty: 2

Question: "What is the write_todos tool used for?"

Expected Answer: "The write_todos tool is provided by TodoListMiddleware and
enables agents to create and update a todo list for planning complex,
multi-part tasks."

--- FileSearch ---
Answer: "The write_todos tool helps agents break down tasks..."
Correctness: 5
Completeness: 4
Relevance: 5
Citation: 3
Total: 4.25
Time: 2.1s
Tokens: 856

--- VectorStore ---
Answer: "write_todos is a planning tool..."
Correctness: 5
Completeness: 3
Relevance: 5
Citation: 4
Total: 4.25
Time: 3.8s
Tokens: 1243

Winner: TIE
```

---

## Part 7: Evaluation Quality Control

### Inter-Rater Reliability

**When using multiple evaluators:**
```
Cohen's Kappa = Measure of agreement between raters
κ > 0.8: Excellent agreement
κ > 0.6: Good agreement
κ < 0.4: Poor agreement (recalibrate)
```

### LLM-Judge Validation

**Validate LLM scoring:**
- Human evaluates 10% sample
- Compare human vs LLM scores
- Correlation should be r > 0.85
- Recalibrate prompts if needed

---

## Part 8: Actionable Insights

### Decision Matrix

Based on metrics, create decision guidance:

```
USE FILESEARCH WHEN:
✅ Exact keyword queries (Mean: 4.5 vs 3.2)
✅ Structured data retrieval (Mean: 4.2 vs 3.5)
✅ Speed critical (3.2s vs 4.8s)
✅ Cost sensitive ($0.05 vs $0.08)
✅ Factual precision needed (4.3 vs 3.8)

USE VECTOR STORE WHEN:
✅ Semantic/conceptual queries (Mean: 4.5 vs 2.7)
✅ Multi-hop reasoning (Mean: 4.3 vs 2.5)
✅ Synonym/paraphrase handling (Mean: 4.6 vs 2.8)
✅ High recall critical (0.84 vs 0.68)
✅ Natural language queries

USE HYBRID WHEN:
✅ Best of both needed
✅ Diverse query types
✅ Accuracy priority over cost/speed
```

---

## Best Practices for Metrics

### Do's ✅
- Report confidence intervals
- Use multiple metrics (no single metric tells all)
- Consider both accuracy and efficiency
- Perform statistical significance tests
- Analyze failure modes qualitatively

### Don'ts ❌
- Don't report mean without standard deviation
- Don't ignore statistical significance
- Don't cherry-pick favorable metrics
- Don't forget cost considerations
- Don't overlook qualitative insights

---

**Next:** See [question_template.md](question_template.md) for creating test questions with proper ground truth and scoring criteria.
