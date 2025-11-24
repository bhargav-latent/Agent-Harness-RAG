# Question Template for RAG Evaluation

> **Template and guidelines for creating high-quality evaluation questions**

## Question Format (YAML)

```yaml
question_id: "Q001"
category: "exact_match"  # See categories.md for options
difficulty: 2  # 1-5 scale
status: "active"  # active, draft, deprecated

# The Question
question_text: |
  What is the write_todos tool used for?

# Ground Truth
expected_answer: |
  The write_todos tool is provided by TodoListMiddleware and enables agents
  to create and update a todo list for planning and tracking progress on
  complex, multi-part tasks. It helps agents break down tasks into discrete
  steps and adapt plans dynamically.

# Source Attribution
expected_sources:
  - document: "CLAUDE.md"
    section: "Middleware System > TodoListMiddleware"
    page: null
    relevant: true
    direct: true
  - document: "CLAUDE.md"
    section: "Best Practices > Planning and Decomposition"
    page: null
    relevant: true
    direct: false

# Evaluation Criteria
evaluation_criteria:
  correctness:
    required_facts:
      - "write_todos is a tool"
      - "provided by TodoListMiddleware"
      - "used for planning and task decomposition"
    optional_facts:
      - "helps track progress"
      - "enables dynamic adaptation"
    incorrect_if:
      - "claims it's from different middleware"
      - "wrong purpose stated"

  completeness:
    minimum_coverage:
      - "tool identification"
      - "source middleware"
      - "primary purpose"
    full_coverage:
      - "all above"
      - "use cases"
      - "benefits"

  relevance:
    on_topic: true
    acceptable_scope: "focused on write_todos tool only"
    off_topic_examples:
      - "discussing other middleware"
      - "general planning discussion without tool focus"

  citation:
    minimum: "mention CLAUDE.md or documentation"
    ideal: "specific section reference (TodoListMiddleware)"

# Expected Retrieval
expected_retrieval:
  filesearch:
    likely_success: true
    search_terms: ["write_todos", "TodoListMiddleware"]
    expected_docs: 1-2

  vectorstore:
    likely_success: true
    semantic_concepts: ["planning", "task management", "todo list"]
    expected_docs: 3-5

# Metadata
created_date: "2025-11-24"
created_by: "framework_designer"
reviewed: false
reviewer: null
review_date: null

notes: |
  This is a straightforward factual question testing basic knowledge
  retrieval. Both methods should handle well. Good baseline question.
```

---

## Field Descriptions

### Core Fields

#### `question_id`
- **Format:** "Q" + 3-digit number (Q001, Q002, etc.)
- **Uniqueness:** Must be unique across all questions
- **Sorting:** Questions will be ordered by ID

#### `category`
- **Options:** See categories.md for 12 valid categories
- **Required:** Must match exactly one category
- **Primary only:** If spans multiple, choose most relevant

#### `difficulty`
- **Scale:** 1-5 integer
- **1 (Easy):** Simple fact lookup
- **2 (Medium):** Straightforward but requires understanding
- **3 (Moderate):** Multi-step or synthesis required
- **4 (Hard):** Complex reasoning or deep knowledge
- **5 (Expert):** Very challenging, edge cases

#### `status`
- **active:** Ready for use in evaluation
- **draft:** Work in progress
- **deprecated:** No longer used

---

### Question Content

#### `question_text`
- **Natural language:** As a real user would ask
- **Clear and specific:** Avoid ambiguity
- **Self-contained:** Don't require prior context
- **Varied phrasing:** Use different question styles

**Good Examples:**
- "What is the purpose of StateBackend?"
- "How do subagents maintain context isolation?"
- "Compare TodoListMiddleware and FilesystemMiddleware"

**Bad Examples:**
- "Explain everything about backends" (too broad)
- "What about the thing mentioned earlier?" (needs context)
- "Backend?" (too vague)

---

### Ground Truth

#### `expected_answer`
- **Comprehensive:** Cover all key aspects
- **Accurate:** Factually correct, verifiable
- **Well-structured:** Clear and organized
- **Cited:** Based on actual corpus content
- **Length:** 2-4 sentences for simple, 1-2 paragraphs for complex

**Guidelines:**
- Write as if you're the ideal RAG system
- Include main points that must be covered
- Don't need to be exhaustive (that's for evaluation criteria)
- Use similar level of detail as expected from system

---

### Source Attribution

#### `expected_sources`
Each source has:
- **document:** Filename (e.g., "CLAUDE.md", "attention_is_all_you_need.pdf")
- **section:** Section or chapter title if applicable
- **page:** Page number for PDFs, null for markdown
- **relevant:** Boolean - is this source relevant?
- **direct:** Boolean - does it directly answer the question?

**Direct vs. Supporting Sources:**
- **Direct:** Contains the explicit answer
- **Supporting:** Provides context or related information

**Example:**
```yaml
expected_sources:
  # Direct source - explicitly answers question
  - document: "CLAUDE.md"
    section: "Backend Storage > StateBackend"
    relevant: true
    direct: true

  # Supporting source - provides related context
  - document: "CLAUDE.md"
    section: "Backend Storage > CompositeBackend"
    relevant: true
    direct: false
```

---

### Evaluation Criteria

This section guides scoring. Be explicit about what makes an answer good/bad.

#### `correctness`

**required_facts:** Must be present for high score
```yaml
required_facts:
  - "StateBackend stores files in LangGraph state"
  - "Files are ephemeral to current thread"
  - "No persistence across sessions"
```

**optional_facts:** Nice to have, improve completeness
```yaml
optional_facts:
  - "Fast, in-memory operations"
  - "Default backend option"
  - "Good for temporary scratch work"
```

**incorrect_if:** Automatic low score if present
```yaml
incorrect_if:
  - "StateBackend persists across sessions" (wrong)
  - "StateBackend requires Redis" (wrong)
```

#### `completeness`

**minimum_coverage:** Minimum for passing score (≥3)
```yaml
minimum_coverage:
  - "What StateBackend is"
  - "Key characteristic (ephemeral)"
```

**full_coverage:** All points for excellent score (5)
```yaml
full_coverage:
  - "Definition and purpose"
  - "Characteristics (ephemeral, fast)"
  - "Use cases"
  - "Comparison to alternatives (brief)"
```

#### `relevance`

**on_topic:** Should be true (stays focused on question)

**acceptable_scope:** Define what's in bounds
```yaml
acceptable_scope: |
  Focus on StateBackend specifically. Brief mentions of other
  backends for comparison are acceptable but should not dominate.
```

**off_topic_examples:** What would be considered tangential
```yaml
off_topic_examples:
  - "Long discussion of FilesystemBackend"
  - "General storage theory"
  - "Unrelated middleware discussion"
```

#### `citation`

**minimum:** Lowest acceptable citation level
```yaml
minimum: "Mention 'documentation' or 'CLAUDE.md'"
```

**ideal:** Best citation practice
```yaml
ideal: "CLAUDE.md section 'Backend Storage > StateBackend'"
```

---

### Expected Retrieval

Helps understand expected performance characteristics.

#### `filesearch`

**likely_success:** Boolean - should FileSearch find relevant docs?

**search_terms:** Keywords likely to be used
```yaml
search_terms: ["StateBackend", "ephemeral", "LangGraph state"]
```

**expected_docs:** How many documents should be retrieved
```yaml
expected_docs: 1-3  # Range or specific number
```

#### `vectorstore`

**likely_success:** Boolean - should Vector Store find relevant docs?

**semantic_concepts:** Conceptual themes relevant to retrieval
```yaml
semantic_concepts: ["temporary storage", "session memory", "non-persistent"]
```

**expected_docs:** Typically higher than FileSearch due to semantic matching
```yaml
expected_docs: 3-7
```

---

### Metadata

#### Tracking Fields
```yaml
created_date: "2025-11-24"
created_by: "username or team"
reviewed: false  # Has an expert reviewed this?
reviewer: null
review_date: null
last_modified: "2025-11-24"
version: 1
```

#### `notes`
Free-form notes about the question:
- Why this question is important
- Known challenges or edge cases
- Connection to real-world use cases
- Anything noteworthy for interpretation

---

## Question Creation Workflow

### Step 1: Choose Category and Difficulty

1. Review [categories.md](categories.md)
2. Select category to fill
3. Choose difficulty level (balance across 1-5)

### Step 2: Write the Question

1. Use natural language
2. Be specific and clear
3. Ensure it's answerable from corpus
4. Avoid ambiguity

### Step 3: Research the Answer

1. Find answer in corpus documents
2. Note all relevant sources
3. Write comprehensive expected answer
4. Verify factual accuracy

### Step 4: Define Evaluation Criteria

1. List required facts (correctness)
2. Define minimum vs full coverage (completeness)
3. Specify acceptable scope (relevance)
4. Set citation expectations

### Step 5: Predict Retrieval Behavior

1. What would FileSearch find?
2. What would Vector Store retrieve?
3. Note expected successes/challenges

### Step 6: Review and Validate

1. Have another person read it
2. Verify answer is unambiguous
3. Confirm sources are correct
4. Test with both retrieval methods if possible

---

## Quality Checklist

Before finalizing a question:

**Question Quality:**
- [ ] Clear and unambiguous wording
- [ ] Natural language (how users would ask)
- [ ] Answerable from the corpus
- [ ] Appropriate difficulty rating
- [ ] Correctly categorized

**Ground Truth Quality:**
- [ ] Answer is comprehensive
- [ ] All required facts included
- [ ] Factually accurate
- [ ] Appropriate level of detail
- [ ] Well-structured and clear

**Source Attribution:**
- [ ] All relevant sources identified
- [ ] Direct vs supporting sources marked
- [ ] Specific sections/pages noted
- [ ] Sources actually contain the answer

**Evaluation Criteria:**
- [ ] Required facts explicitly listed
- [ ] Completeness criteria defined
- [ ] Relevance scope specified
- [ ] Citation expectations clear
- [ ] Incorrect statements noted

**Metadata:**
- [ ] Unique question ID
- [ ] Created date and author
- [ ] Notes added if needed
- [ ] Review status accurate

---

## Examples by Category

### Example 1: Exact Match

```yaml
question_id: "Q101"
category: "exact_match"
difficulty: 1

question_text: |
  What is the exact class name for ephemeral storage backend?

expected_answer: |
  StateBackend

expected_sources:
  - document: "CLAUDE.md"
    section: "Backend Storage > StateBackend"
    relevant: true
    direct: true

evaluation_criteria:
  correctness:
    required_facts:
      - "StateBackend" (exact name)
    incorrect_if:
      - "EphemeralBackend"
      - "TemporaryBackend"
```

---

### Example 2: Semantic Similarity

```yaml
question_id: "Q201"
category: "semantic_similarity"
difficulty: 3

question_text: |
  What strategies prevent agents from losing focus during extended tasks?

expected_answer: |
  Deep Agents use several strategies: 1) Planning with todo lists to maintain
  structure, 2) File system operations to offload context from conversation,
  3) Subagents for context isolation on subtasks, and 4) Automatic
  summarization when token limits are approached.

expected_sources:
  - document: "CLAUDE.md"
    section: "Core Concepts"
    relevant: true
    direct: true
  - document: "CLAUDE.md"
    section: "Middleware System"
    relevant: true
    direct: true

evaluation_criteria:
  correctness:
    required_facts:
      - "Planning/todo lists maintain structure"
      - "File system offloads context"
      - "Subagents provide isolation"
    optional_facts:
      - "Automatic summarization"
      - "Prevents context overflow"
```

---

### Example 3: Multi-hop Reasoning

```yaml
question_id: "Q501"
category: "multi_hop_reasoning"
difficulty: 4

question_text: |
  How do subagents use filesystem operations to maintain context isolation
  in Deep Agents?

expected_answer: |
  Subagents maintain context isolation through filesystem operations by:
  1) Writing their intermediate results to files rather than keeping in
  conversation history, 2) Only returning final summaries to the main agent,
  not all intermediate tool outputs, 3) Using FilesystemMiddleware tools
  (write_file, read_file) to store large outputs externally, preventing the
  main agent's context from being overwhelmed with subtask details.

expected_sources:
  - document: "CLAUDE.md"
    section: "Subagents"
    relevant: true
    direct: true
  - document: "CLAUDE.md"
    section: "Middleware System > FilesystemMiddleware"
    relevant: true
    direct: true
  - document: "CLAUDE.md"
    section: "Best Practices > Context Management"
    relevant: true
    direct: false

evaluation_criteria:
  correctness:
    required_facts:
      - "Subagents write to files"
      - "Only return final results to main agent"
      - "Prevents context overflow"
    optional_facts:
      - "Uses FilesystemMiddleware"
      - "Intermediate outputs stored externally"

  completeness:
    minimum_coverage:
      - "Connection between subagents and filesystem"
      - "How it achieves isolation"
    full_coverage:
      - "All above"
      - "Specific tools mentioned"
      - "Benefits explained"
```

---

## Tips for Good Questions

### Diversity
- ✅ Vary question styles (what, how, why, compare)
- ✅ Mix short and long questions
- ✅ Include edge cases and corner cases
- ✅ Cover different parts of the corpus

### Clarity
- ✅ Use clear, unambiguous language
- ✅ Define terms if potentially confusing
- ✅ One main question per item
- ❌ Avoid compound questions that ask multiple things

### Realism
- ✅ Ask questions real users would ask
- ✅ Use natural language, not technical queries
- ✅ Consider actual use cases
- ❌ Don't create artificial or contrived questions

### Answerability
- ✅ Ensure answer exists in corpus
- ✅ Verify sources before finalizing
- ✅ Test that it's not too easy or impossibly hard
- ❌ Don't ask questions requiring external knowledge

---

## Version Control

Questions should be versioned:
```yaml
version_history:
  - version: 1
    date: "2025-11-24"
    changes: "Initial creation"
  - version: 2
    date: "2025-11-25"
    changes: "Clarified evaluation criteria after initial testing"
```

---

## Next Steps

1. **Create questions** using this template
2. **Organize by category** in `evaluation/questions/` folder
3. **Review by expert** before use in evaluation
4. **Test with both methods** to validate difficulty
5. **Iterate based on results** and refine as needed

**File Organization:**
```
evaluation/questions/
├── exact_match.yaml          # 5 questions
├── semantic_similarity.yaml  # 6 questions
├── table_data.yaml          # 4 questions
└── ... (one file per category)
```

---

**References:**
- [categories.md](categories.md) - Category definitions
- [metrics.md](metrics.md) - Scoring rubrics
- [framework.md](framework.md) - Overall methodology
