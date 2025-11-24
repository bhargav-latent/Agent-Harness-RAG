# Evaluation Categories

> **Detailed specifications for all 12 evaluation categories**

## Category Overview

Each category tests specific retrieval and generation capabilities. Categories are designed to:
- Expose strengths and weaknesses of each method
- Cover diverse real-world use cases
- Enable targeted performance analysis
- Guide hybrid strategy development

---

## Category 1: Exact Match / Keyword Search

### Purpose
Test precision for finding specific terms, codes, identifiers, and exact phrases.

### Characteristics
- **Query Type:** Specific keywords, proper nouns, error codes, function names
- **Expected Behavior:** Find documents with exact string matches
- **FileSearch Strength:** High (this is core functionality)
- **Vector Store Strength:** Medium (may find but with noise)

### Question Count
5 questions (10% of total)

### Difficulty Range
Level 1-3 (Easy to Moderate)

### Example Question Patterns

**Pattern 1: Technical Term Lookup**
- "What is the definition of [specific term]?"
- "Find references to [exact class/function name]"
- "Locate [specific error code]"

**Pattern 2: Exact Quote Finding**
- "Find the sentence containing '[exact phrase]'"
- "What document mentions '[specific text]'?"

**Pattern 3: Identifier Search**
- "Find function named [exact name]"
- "Locate variable [exact identifier]"
- "Search for endpoint '[exact URL]'"

### Evaluation Criteria

**Correctness Focus:**
- Found the exact term/phrase
- Retrieved correct document
- Accurate surrounding context

**Success Indicators:**
- ✅ Exact match found
- ✅ Correct source identified
- ✅ Minimal false positives

**Failure Modes:**
- ❌ FileSearch: Case sensitivity issues, regex problems
- ❌ Vector Store: Too many semantic neighbors, diluted precision

### Ground Truth Requirements
- Exact location of term in corpus (file, page, line)
- Exact string to match
- Acceptable context variations

---

## Category 2: Semantic Similarity

### Purpose
Test understanding of meaning despite different wording, synonyms, and paraphrasing.

### Characteristics
- **Query Type:** Natural language with varied terminology
- **Expected Behavior:** Find conceptually similar content regardless of exact words
- **FileSearch Strength:** Low (limited to synonyms explicitly present)
- **Vector Store Strength:** High (core semantic understanding)

### Question Count
6 questions (12% of total)

### Difficulty Range
Level 2-4 (Medium to Hard)

### Example Question Patterns

**Pattern 1: Synonym Variations**
- Multiple ways to ask same question
- "How to prevent unauthorized access?" vs "Security best practices"
- "Machine learning model training" vs "Neural network optimization"

**Pattern 2: Conceptual Equivalence**
- "What's the cheapest option?" vs "Most cost-effective solution"
- "Error handling" vs "Fault tolerance" vs "Resilience"

**Pattern 3: Abstraction Levels**
- "How does authentication work?" (broad)
- "Explain identity verification mechanisms" (specific)
- Both should retrieve similar relevant content

### Evaluation Criteria

**Correctness Focus:**
- Understanding core meaning
- Finding conceptually relevant docs
- Not requiring exact keywords

**Success Indicators:**
- ✅ Retrieves semantically similar content
- ✅ Handles synonym variations
- ✅ Understands query intent

**Failure Modes:**
- ❌ FileSearch: Misses content without exact keywords
- ❌ Vector Store: Sometimes too broad, semantic drift

### Ground Truth Requirements
- List of semantically equivalent queries
- All documents that address the concept
- Core meaning to be preserved

---

## Category 3: Table & Structured Data Retrieval

### Purpose
Test extraction of information from tables, comparison matrices, and structured formats.

### Characteristics
- **Query Type:** Comparative questions, "what are the differences", listing requests
- **Expected Behavior:** Extract and present structured information accurately
- **FileSearch Strength:** High (can extract table text)
- **Vector Store Strength:** Medium (may lose structure in embeddings)

### Question Count
4 questions (8% of total)

### Difficulty Range
Level 2-4 (Medium to Hard)

### Example Question Patterns

**Pattern 1: Comparison Queries**
- "Compare X and Y"
- "What are the differences between A and B?"
- "List advantages and disadvantages of Z"

**Pattern 2: Table Lookup**
- "What are the features of [component]?"
- "List all [item types] and their properties"
- "Show metrics for [system]"

**Pattern 3: Structured Extraction**
- "What backends support persistence?"
- "Which middleware provides which tools?"
- "List all models and their token limits"

### Evaluation Criteria

**Correctness Focus:**
- Accurate extraction of structured data
- Preservation of comparisons
- Complete information coverage

**Success Indicators:**
- ✅ All table cells/rows retrieved
- ✅ Structure preserved or reconstructed
- ✅ Comparisons accurately represented

**Failure Modes:**
- ❌ FileSearch: May retrieve table as plain text (hard to parse)
- ❌ Vector Store: May lose tabular structure in embeddings

### Ground Truth Requirements
- Exact table from source
- All relevant rows/columns
- Expected format in answer

---

## Category 4: Formulas & Mathematical Content

### Purpose
Test retrieval of equations, mathematical expressions, and algorithmic content.

### Characteristics
- **Query Type:** "What is the formula for", "How to calculate", algorithm requests
- **Expected Behavior:** Retrieve mathematical content with notation intact
- **FileSearch Strength:** High (can find LaTeX, exact notation)
- **Vector Store Strength:** Medium (embeddings may not preserve math structure)

### Question Count
4 questions (8% of total)

### Difficulty Range
Level 2-4 (Medium to Hard)

### Example Question Patterns

**Pattern 1: Formula Requests**
- "What is the formula for [concept]?"
- "How is [metric] calculated?"
- "Show the equation for [algorithm]"

**Pattern 2: Mathematical Explanation**
- "Explain the calculation of [quantity]"
- "How does [algorithm] compute [output]?"

**Pattern 3: Specific Notation**
- "What is the softmax function?"
- "Show the attention score equation"

### Evaluation Criteria

**Correctness Focus:**
- Formula accuracy
- Notation preservation
- Complete expression

**Success Indicators:**
- ✅ Correct mathematical formula
- ✅ Notation readable/clear
- ✅ Variables explained

**Failure Modes:**
- ❌ FileSearch: May find but formatting lost in extraction
- ❌ Vector Store: May paraphrase instead of exact formula

### Ground Truth Requirements
- Exact formula from source
- Expected notation format
- Variable definitions

---

## Category 5: Multi-hop Reasoning

### Purpose
Test questions requiring information synthesis from multiple sources or sections.

### Characteristics
- **Query Type:** Complex questions spanning topics, "explain the relationship", workflows
- **Expected Behavior:** Retrieve multiple relevant pieces and synthesize
- **FileSearch Strength:** Low (hard to identify what to combine)
- **Vector Store Strength:** High (can find related concepts across docs)

### Question Count
5 questions (10% of total)

### Difficulty Range
Level 3-5 (Moderate to Expert)

### Example Question Patterns

**Pattern 1: Component Interaction**
- "How does X use Y to accomplish Z?"
- "Explain the relationship between A and B"
- "How do components work together?"

**Pattern 2: Workflow Questions**
- "Describe the full process from start to end"
- "What happens when X triggers Y?"

**Pattern 3: Cross-Document Synthesis**
- "How does concept from doc A relate to doc B?"
- "What do multiple sources say about X?"

### Evaluation Criteria

**Correctness Focus:**
- Synthesis of multiple sources
- Logical connections made
- Complete workflow described

**Success Indicators:**
- ✅ Multiple relevant sources retrieved
- ✅ Connections properly explained
- ✅ Complete narrative constructed

**Failure Modes:**
- ❌ FileSearch: Finds pieces but misses connections
- ❌ Vector Store: May miss specific details while getting concepts

### Ground Truth Requirements
- All documents needed
- Key connections to make
- Expected synthesis

---

## Category 6: Code Understanding

### Purpose
Test finding and explaining code snippets, patterns, and implementations.

### Characteristics
- **Query Type:** Code search, implementation requests, pattern finding
- **Expected Behavior:** Find relevant code and explain appropriately
- **FileSearch Strength:** Medium (can find code by keywords)
- **Vector Store Strength:** High (can understand code semantics)

### Question Count
4 questions (8% of total)

### Difficulty Range
Level 2-4 (Medium to Hard)

### Example Question Patterns

**Pattern 1: Code Search by Purpose**
- "Find code that does X"
- "Show me implementation of Y"
- "Example of Z pattern"

**Pattern 2: Code Explanation**
- "How does this code work?"
- "Explain the implementation of X"

**Pattern 3: Pattern Matching**
- "Find similar code patterns"
- "Show examples of X pattern usage"

### Evaluation Criteria

**Correctness Focus:**
- Relevant code found
- Proper explanation
- Context provided

**Success Indicators:**
- ✅ Correct code snippet retrieved
- ✅ Purpose/function explained
- ✅ Usage context provided

**Failure Modes:**
- ❌ FileSearch: May find wrong code with similar keywords
- ❌ Vector Store: May find semantically similar but wrong language/pattern

### Ground Truth Requirements
- Expected code snippets
- Correct explanation
- Source location

---

## Category 7: Acronyms & Abbreviations

### Purpose
Test bridging between technical shorthand and full terminology.

### Characteristics
- **Query Type:** "What is [acronym]?", "What does [abbreviation] mean?"
- **Expected Behavior:** Find full term even if query uses acronym or vice versa
- **FileSearch Strength:** Low (exact match only)
- **Vector Store Strength:** High (embeddings connect related terms)

### Question Count
3 questions (6% of total)

### Difficulty Range
Level 1-3 (Easy to Moderate)

### Example Question Patterns

**Pattern 1: Acronym Expansion**
- "What is RAG?"
- "What does NDCG mean?"
- "Explain MRR metric"

**Pattern 2: Abbreviation Usage**
- "Find information about GPT"
- "What is LLM?"

**Pattern 3: Bidirectional Search**
- Query "neural network" should find "NN"
- Query "API" should find "Application Programming Interface"

### Evaluation Criteria

**Correctness Focus:**
- Correct expansion/definition
- Relevant context provided
- Both forms connected

**Success Indicators:**
- ✅ Acronym correctly expanded
- ✅ Full term found when acronym queried
- ✅ Proper definition provided

**Failure Modes:**
- ❌ FileSearch: Misses if exact form not in query
- ❌ Vector Store: May confuse similar acronyms

### Ground Truth Requirements
- Acronym and full term
- Official definition
- Context of usage

---

## Category 8: Contextual Disambiguation

### Purpose
Test understanding of polysemous terms (same word, different meanings in different contexts).

### Characteristics
- **Query Type:** Ambiguous terms that need context interpretation
- **Expected Behavior:** Understand intended meaning from context
- **FileSearch Strength:** Low (returns all matches without discrimination)
- **Vector Store Strength:** High (can use context to disambiguate)

### Question Count
4 questions (8% of total)

### Difficulty Range
Level 3-5 (Moderate to Expert)

### Example Question Patterns

**Pattern 1: Polysemous Terms**
- "What is 'store'?" (backend vs. vector store vs. LangGraph Store)
- "Explain 'agent'" (main vs. subagent vs. general agent)
- "Define 'tool'" (function vs. middleware vs. system)

**Pattern 2: Context-Dependent Meaning**
- "What does 'memory' mean?" (file vs. LLM context vs. persistent)
- "What is 'state'?" (LangGraph state vs. application state)

### Evaluation Criteria

**Correctness Focus:**
- Correct interpretation selected
- Appropriate context used
- Ambiguity addressed

**Success Indicators:**
- ✅ Correct meaning identified
- ✅ Context-appropriate answer
- ✅ Ambiguity acknowledged if needed

**Failure Modes:**
- ❌ FileSearch: Returns all matches without ranking by context
- ❌ Vector Store: May still be ambiguous without clear context

### Ground Truth Requirements
- All possible meanings
- Context clues for each
- Expected interpretation

---

## Category 9: Negation & Exclusion Queries

### Purpose
Test understanding of negative queries with "not", "without", "except", "excluding".

### Characteristics
- **Query Type:** Questions with negations or exclusions
- **Expected Behavior:** Properly filter based on negative constraints
- **FileSearch Strength:** Medium (can use negative flags)
- **Vector Store Strength:** Medium (embeddings may not capture negation well)

### Question Count
3 questions (6% of total)

### Difficulty Range
Level 3-4 (Moderate to Hard)

### Example Question Patterns

**Pattern 1: Explicit Negation**
- "What backends don't support persistence?"
- "Which methods cannot handle X?"
- "Find options without Y"

**Pattern 2: Exclusion**
- "All except X"
- "Everything but Y"
- "Excluding Z, what remains?"

**Pattern 3: Absence Queries**
- "What is missing in X?"
- "What doesn't Y provide?"

### Evaluation Criteria

**Correctness Focus:**
- Proper negation handling
- Correct exclusion applied
- Complete inverse set

**Success Indicators:**
- ✅ Negation correctly applied
- ✅ Excluded items not in answer
- ✅ Remaining items all included

**Failure Modes:**
- ❌ FileSearch: May miss negation logic
- ❌ Vector Store: Embeddings may not strongly represent negation

### Ground Truth Requirements
- Complete set of items
- Excluded subset
- Expected remaining items

---

## Category 10: Temporal & Version Information

### Purpose
Test time-based queries, versioning, and recency-aware retrieval.

### Characteristics
- **Query Type:** "When", "latest", "recent", "deprecated", version-specific
- **Expected Behavior:** Find time-relevant or version-specific information
- **FileSearch Strength:** Medium (can find dates/versions)
- **Vector Store Strength:** Medium (depends on metadata)

### Question Count
3 questions (6% of total)

### Difficulty Range
Level 2-4 (Medium to Hard)

### Example Question Patterns

**Pattern 1: Recency**
- "What's new in latest version?"
- "Recent changes to X"
- "Latest updates"

**Pattern 2: Historical**
- "When was X introduced?"
- "What year was Y published?"
- "Original version of Z"

**Pattern 3: Version-Specific**
- "What changed in v2.0?"
- "Features deprecated since X"

### Evaluation Criteria

**Correctness Focus:**
- Correct temporal information
- Accurate version details
- Recency properly handled

**Success Indicators:**
- ✅ Correct date/version found
- ✅ Appropriate temporal context
- ✅ Version differences identified

**Failure Modes:**
- ❌ FileSearch: May find dates but not understand recency
- ❌ Vector Store: May lack temporal metadata

### Ground Truth Requirements
- Exact dates/versions
- Temporal context
- Version history if applicable

---

## Category 11: Factual Precision

### Purpose
Test retrieval of exact facts: numbers, dates, names, specifications.

### Characteristics
- **Query Type:** Specific factual questions requiring precise answers
- **Expected Behavior:** Provide exactly correct factual information
- **FileSearch Strength:** High (good at exact matches)
- **Vector Store Strength:** Medium (may approximate)

### Question Count
4 questions (8% of total)

### Difficulty Range
Level 1-3 (Easy to Moderate)

### Example Question Patterns

**Pattern 1: Numerical Facts**
- "What is the token limit for X?"
- "How many Y are there?"
- "What is the size of Z?"

**Pattern 2: Names & Entities**
- "Who authored X?"
- "What is the name of Y?"
- "List contributors to Z"

**Pattern 3: Specifications**
- "What are the dimensions of X?"
- "What is the configuration for Y?"

### Evaluation Criteria

**Correctness Focus:**
- Exact factual accuracy
- Precise numbers/names
- No approximation acceptable

**Success Indicators:**
- ✅ Exact fact retrieved
- ✅ No errors in details
- ✅ Properly cited

**Failure Modes:**
- ❌ FileSearch: Good at this, rare failures
- ❌ Vector Store: May approximate or round

### Ground Truth Requirements
- Exact factual answer
- Source location
- No acceptable variations

---

## Category 12: Conceptual / Abstract Queries

### Purpose
Test high-level understanding, "why", "how", philosophy, and design rationale.

### Characteristics
- **Query Type:** Conceptual, explanatory, design questions
- **Expected Behavior:** Provide understanding of concepts and rationale
- **FileSearch Strength:** Low (hard to find without right keywords)
- **Vector Store Strength:** High (good at conceptual matching)

### Question Count
5 questions (10% of total)

### Difficulty Range
Level 3-5 (Moderate to Expert)

### Example Question Patterns

**Pattern 1: Why Questions**
- "Why use X instead of Y?"
- "What problem does Z solve?"
- "Why is this approach chosen?"

**Pattern 2: How Questions**
- "How does X prevent Y?"
- "How does this design achieve Z?"

**Pattern 3: Philosophy**
- "What is the philosophy behind X?"
- "Explain the design principles of Y"

### Evaluation Criteria

**Correctness Focus:**
- Conceptual understanding
- Design rationale explained
- Trade-offs discussed

**Success Indicators:**
- ✅ Concept properly explained
- ✅ Rationale provided
- ✅ Trade-offs mentioned

**Failure Modes:**
- ❌ FileSearch: May miss without exact keywords
- ❌ Vector Store: May be too general

### Ground Truth Requirements
- Core concept explanation
- Design rationale
- Expected depth of understanding

---

## Category Selection Guidelines

### When Creating Questions

**For Each Category:**
1. Understand the specific capability being tested
2. Ensure questions clearly belong to that category
3. Vary difficulty within category
4. Include edge cases where appropriate
5. Ensure ground truth is unambiguous

**Cross-Category Considerations:**
- Some questions may span multiple categories
- Assign to primary category
- Note secondary categories in metadata
- Use for multi-dimensional analysis

### Distribution Rationale

**Higher Count (5-6 questions):**
- Semantic Similarity - Core differentiator
- Multi-hop Reasoning - Complex capability
- Conceptual/Abstract - High-level understanding

**Medium Count (4 questions):**
- Tables, Formulas, Code - Important but specific
- Contextual Disambiguation - Challenging edge cases
- Factual Precision - Critical for trust

**Lower Count (3 questions):**
- Acronyms - Specific but common
- Negation - Edge case handling
- Temporal - Metadata-dependent

---

## Usage in Evaluation

### During Test Creation
- Refer to this document for each question
- Ensure category assignment is correct
- Follow example patterns
- Note expected strengths/weaknesses

### During Analysis
- Group results by category
- Compare category-level performance
- Identify patterns in strengths/weaknesses
- Inform hybrid strategy design

### During Reporting
- Present category-by-category comparison
- Highlight where each method excels
- Map categories to use cases
- Guide deployment decisions

---

**Next:** See [metrics.md](metrics.md) for detailed scoring rubrics and [question_template.md](question_template.md) for creating questions.
