# FileSearch RAG Implementation

This directory contains the FileSearch RAG implementation using LangChain.

## Files

### filesearch_rag.py
Core FileSearch RAG agent implementation using:
- LangChain agents framework
- Custom tools for file operations (grep, glob, read_file)
- Local LLM endpoint (Qwen 235B)

### run_evaluation.py
Evaluation runner that:
- Loads evaluation dataset (JSONL)
- Runs questions through FileSearch RAG
- Measures Correctness, Latency, Cost
- Saves results for analysis

## Setup

### 1. Create `.env` file

Copy `.env.template` to `.env` and verify the settings:

```bash
cp ../.env.template ../.env
```

The default configuration points to:
- LLM: `http://10.26.1.56:8708/v1` (Qwen 235B)
- Documents: `./rag_data/processed`

### 2. Verify dependencies

Ensure you have activated your virtual environment and installed requirements:

```bash
# Activate venv (if not already active)
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate  # Windows

# Verify installation
python -c "import langchain; print('LangChain installed')"
```

## Usage

### Quick Test

Test the FileSearch RAG with a single question:

```bash
python filesearch_rag.py
```

This will run a sample question: "What is the value of dmodel used in the Transformer architecture?"

### Run Evaluation

Evaluate all 50 questions:

```bash
python run_evaluation.py
```

**Options:**

```bash
# Limit to first 5 questions (for testing)
python run_evaluation.py --limit 5

# Filter by categories
python run_evaluation.py --categories exact_match semantic

# Custom output filename
python run_evaluation.py --output my_test_results.jsonl

# Combine options
python run_evaluation.py --limit 10 --categories exact_match table_data
```

### Results

Results are saved to `../evaluation/results/` with format:
- Filename: `filesearch_results_YYYYMMDD_HHMMSS.jsonl`
- Format: One JSON object per line (JSONL)
- Contains: question, answer, retrieved_contexts, metrics

## Architecture

### FileSearch RAG Flow

```
User Question
     ↓
Agent (LangChain)
     ↓
Planning & Tool Selection
     ↓
Tools:
  - list_documents: List available markdown files
  - search_content: Grep-like search across documents
  - read_document: Read specific files or line ranges
  - search_in_document: Search within specific file with context
     ↓
Context Retrieved
     ↓
LLM Generation (Qwen 235B)
     ↓
Answer with Citations
```

### Key Features

1. **Strategic Search**: Agent plans searches using keyword matching
2. **Targeted Reading**: Only reads relevant sections to manage context
3. **Citation Support**: Tracks which documents and sections were used
4. **Error Handling**: Graceful fallbacks for missing files or failed searches
5. **Context Management**: Limits output size to prevent context overflow

## Tools

### 1. list_documents
- **Purpose**: Discover available documents
- **Usage**: `list_documents(pattern="*.md")`
- **Returns**: Filenames with sizes

### 2. search_content
- **Purpose**: Search across all documents (grep-like)
- **Usage**: `search_content(keyword="Transformer")`
- **Returns**: Matching lines with file:line_num format
- **Features**: Case-insensitive, limits to 20 matches

### 3. read_document
- **Purpose**: Read file content
- **Usage**: `read_document(filename="attention_is_all_you_need.md")`
- **Options**:
  - Read entire file (auto-truncated if >10KB)
  - Read specific lines: `read_document(filename, start_line=100, num_lines=50)`
- **Returns**: File content

### 4. search_in_document
- **Purpose**: Search within specific document with context
- **Usage**: `search_in_document(filename="...", keyword="...", context_lines=2)`
- **Returns**: Matching sections with surrounding lines
- **Best for**: Finding exact formulas, code, or quotes

## Evaluation Metrics

The evaluation runner computes:

### 1. Latency
- Measured in milliseconds
- Includes search + retrieval + generation time
- **Target**: < 3000ms per question

### 2. Success Rate
- Percentage of questions successfully answered
- Tracks failures due to errors or timeouts
- **Target**: > 95%

### 3. By Category Performance
- Success rate for each of the 12 question categories
- Identifies which types of questions work best
- **Example**: "exact_match: 100%, semantic: 85%"

## Troubleshooting

### Issue: "Connection refused" to LLM endpoint

**Solution**: Verify the LLM service is running:
```bash
curl http://10.26.1.56:8708/v1/models
```

If not accessible, update `LLM_BASE_URL` in `.env` file.

### Issue: "Documents directory not found"

**Solution**: Verify the path in `.env`:
```bash
DOCUMENTS_DIR=./rag_data/processed
```

Check that markdown files exist:
```bash
ls -la ../rag_data/processed/
```

### Issue: Agent takes too long or times out

**Solution**:
1. Reduce `max_iterations` in `filesearch_rag.py` (default: 10)
2. Use `--limit` flag to test fewer questions first
3. Check if LLM endpoint is responding slowly

### Issue: "No matches found" for valid questions

**Possible causes**:
1. Keyword too specific - agent should try variations
2. Documents not preprocessed - check `rag_data/processed/` has .md files
3. File encoding issues - verify files are UTF-8

**Debug**: Run with a simple known query:
```bash
python filesearch_rag.py
```

## Next Steps

After running FileSearch RAG evaluation:

1. **Analyze Results**: Review `evaluation/results/*.jsonl`
2. **Compare**: Build Vector Store RAG and run same evaluation
3. **Visualize**: Create comparison charts (Correctness, Latency, Cost)
4. **Decide**: Choose best approach or hybrid strategy

## Performance Tips

### For Faster Evaluation:
1. Use `--limit 10` to test subset first
2. Start with easy categories: `--categories exact_match factual`
3. Monitor agent verbose output to see search strategy

### For Better Accuracy:
1. Agent should try multiple search terms if first fails
2. Use `search_in_document` for precise extraction
3. Read specific line ranges to get context without overflow

### For Lower Cost:
1. Limit tool iterations (reduce context sent to LLM)
2. Use smaller context windows in `read_document`
3. Cache common searches (future enhancement)

## References

- [LangChain Agents Documentation](https://python.langchain.com/docs/modules/agents/)
- [OpenAI Tools Agent](https://python.langchain.com/docs/modules/agents/agent_types/openai_tools/)
- [Project README](../README.md)
- [Evaluation Framework](../evaluation/framework.md)
