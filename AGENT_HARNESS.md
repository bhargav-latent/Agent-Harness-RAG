# Agent Harness Architecture

> **Purpose:** File search and question answering system using terminal-based RAG with Deep Agents framework

## Overview

This agent harness uses LangChain Deep Agents to systematically search through files and answer questions. The primary approach is **FileSearch RAG** (terminal-based) rather than vector embeddings.

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│              Main Agent (Qwen 235B)                  │
│  - Plan tasks with TodoListMiddleware               │
│  - Search files with FilesystemMiddleware           │
│  - Answer questions from file content               │
└─────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────┐
│                  Middleware Layer                    │
│  ┌──────────────────┐  ┌──────────────────┐        │
│  │ TodoListMiddleware│  │FilesystemMiddleware│       │
│  │ (Planning)        │  │ (File Operations) │       │
│  └──────────────────┘  └──────────────────┘        │
└─────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────┐
│                FilesystemBackend                     │
│         (Local disk file operations)                 │
└─────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────┐
│              Document Corpus                         │
│         documents/ folder with PDFs                  │
└─────────────────────────────────────────────────────┘
```

---

## Components

### 1. Language Model (LLM)

**Model:** Qwen/Qwen3-235B-A22B-Instruct-2507-FP8
**Endpoint:** `http://10.26.1.56:8708/v1`
**Configuration:**
- Temperature: 0.7
- Max Tokens: 8192

**Environment Variable:**
```bash
LLM_BASE_URL=http://10.26.1.56:8708/v1
LLM_MODEL=Qwen/Qwen3-235B-A22B-Instruct-2507-FP8
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=8192
```

---

### 2. Embeddings Model

**Model:** Qwen/Qwen3-Embedding-8B
**Endpoint:** `http://10.26.1.56:8786/v1/embeddings`
**Note:** Different port (8786) than LLM

**Environment Variable:**
```bash
EMBEDDINGS_BASE_URL=http://10.26.1.56:8786/v1/embeddings
EMBEDDINGS_MODEL=Qwen/Qwen3-Embedding-8B
```

---

### 3. Middleware

#### TodoListMiddleware
**Purpose:** Task planning and progress tracking
**Tool:** `write_todos`
**Usage:** Agent breaks down complex queries into steps

**Reference:** [Deep Agents Middleware - TodoList](https://docs.langchain.com/oss/python/deepagents/middleware#todolistmiddleware)

#### FilesystemMiddleware
**Purpose:** File operations and content access
**Tools:**
- `ls` - List files and directories
- `read_file` - Read file contents
- `write_file` - Write data to files
- `edit_file` - Modify existing files
- `grep` - Search content across files
- `glob` - Pattern-based file matching

**Reference:** [Deep Agents Middleware - Filesystem](https://docs.langchain.com/oss/python/deepagents/middleware#filesystemmiddleware)

---

### 4. Backend Storage

**Backend:** FilesystemBackend
**Purpose:** Direct file operations on local disk
**Configuration:**
- Root directory: `./workspace` (or project root)
- Virtual mode: Enabled (sandboxed paths)
- Direct access to `documents/` folder

**Reference:** [Deep Agents Backends - FilesystemBackend](https://docs.langchain.com/oss/python/deepagents/backends#filesystembackend)

---

### 5. RAG Approach: FileSearch (Terminal-Based)

**Primary Strategy:** Terminal-based file search, NOT vector embeddings

#### Recommended Tools

**Core FileSearch Tools:**
1. **grep** - Content search with regex support
   - Search for keywords across files
   - Context lines (before/after matches)
   - Case-sensitive/insensitive options

2. **glob** - File pattern matching
   - Find files by name patterns
   - Recursive directory search
   - Filter by extensions (*.pdf, *.md)

3. **read_file** - Read specific files
   - Extract full content
   - Targeted reading after search
   - Parse structured content

4. **ls** - Directory listing
   - Explore file structure
   - Identify available documents
   - Navigate directories

**Workflow:**
```
User Query
    ↓
Plan with TodoList (break down query)
    ↓
Search with grep/glob (find relevant files)
    ↓
Read with read_file (extract content)
    ↓
Synthesize Answer
```

**Advantages:**
- ✅ Exact keyword matching
- ✅ Fast for small/medium corpora
- ✅ No embedding overhead
- ✅ Direct file access
- ✅ Transparent search process

---

### 6. Document Corpus

**Location:** `documents/` folder

**Current Documents:**
- `The Essence of Software Engineering, Volker Gruhn, Rudiger Striemer.pdf`
- `attention_is_all_you_need.pdf`
- `thinkpython2.pdf`
- `CLAUDE.md` (Deep Agents documentation)

**Format Support:**
- PDF documents (primary)
- Markdown files
- Text files

---

## Deployment

**Platform:** Local LangGraph CLI
**Mode:** Development/Testing

**Reference:** [LangGraph CLI Documentation](https://langchain-ai.github.io/langgraph/cloud/reference/cli/)

---

## Environment Configuration

Create `.env` file in project root:

```bash
# LLM Configuration
LLM_BASE_URL=http://10.26.1.56:8708/v1
LLM_MODEL=Qwen/Qwen3-235B-A22B-Instruct-2507-FP8
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=8192

# Embeddings Configuration (for future use)
EMBEDDINGS_BASE_URL=http://10.26.1.56:8786/v1/embeddings
EMBEDDINGS_MODEL=Qwen/Qwen3-Embedding-8B

# Filesystem Backend
WORKSPACE_ROOT=./workspace

# LangGraph
LANGGRAPH_ENV=local
```

---

## Agent Capabilities

### What the Agent Can Do

1. **Search Files**
   - Find documents by keywords
   - Search specific content patterns
   - Filter by file type/name

2. **Answer Questions**
   - Extract relevant information
   - Cite source files
   - Synthesize multi-document answers

3. **Plan Complex Queries**
   - Break down multi-part questions
   - Track progress with todos
   - Adapt strategy based on results

4. **Navigate File Structure**
   - List available documents
   - Explore directories
   - Identify relevant sources

### Typical User Workflow

```
User: "What does the transformer paper say about attention mechanisms?"

Agent Process:
1. Plan: Create todos (search files, read relevant sections, synthesize answer)
2. Search: grep for "attention mechanism" in documents/
3. Identify: attention_is_all_you_need.pdf contains answer
4. Read: Extract relevant sections from PDF
5. Answer: Provide explanation with citations
```

---

## References

### Deep Agents Documentation
- **Overview:** https://docs.langchain.com/oss/python/deepagents/overview
- **Harness:** https://docs.langchain.com/oss/python/deepagents/harness
- **Middleware:** https://docs.langchain.com/oss/python/deepagents/middleware
- **Backends:** https://docs.langchain.com/oss/python/deepagents/backends
- **Blog Post:** https://blog.langchain.com/deep-agents/

### LangChain Ecosystem
- **LangGraph:** https://langchain-ai.github.io/langgraph/
- **LangChain:** https://python.langchain.com/
- **LangSmith:** https://smith.langchain.com/

---

## Architecture Decisions

### Why FileSearch RAG?
1. **Simplicity** - No vector database infrastructure needed
2. **Transparency** - Clear search process with grep/glob
3. **Speed** - Fast for small/medium document sets
4. **Accuracy** - Exact keyword matching for technical content
5. **Cost** - No embedding generation overhead

### Why FilesystemBackend?
1. **Direct Access** - Work directly with local files
2. **Development** - Ideal for local testing
3. **Simplicity** - No external storage dependencies
4. **Flexibility** - Easy file manipulation

### Why TodoListMiddleware?
1. **Planning** - Break down complex queries
2. **Tracking** - Monitor progress on multi-step tasks
3. **Transparency** - User sees agent's reasoning

---

## Future Enhancements (Not Current)

For reference, if expanding beyond FileSearch:
- Vector Store RAG comparison (evaluation framework ready)
- Hybrid approach (FileSearch + Vector)
- SubAgents for specialized tasks
- StoreBackend for persistent memory

---

## Summary

**Current Setup:**
- **Agent:** Qwen 235B for reasoning and generation
- **Middleware:** TodoList (planning) + Filesystem (file ops)
- **Backend:** FilesystemBackend (local disk)
- **RAG:** FileSearch using grep/glob/read_file
- **Deployment:** Local LangGraph CLI
- **Use Case:** Systematic file search and question answering

**Key Strength:** Simple, transparent, fast file-based RAG without vector complexity.
