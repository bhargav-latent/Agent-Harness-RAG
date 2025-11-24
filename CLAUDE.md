# CLAUDE.md - AI Assistant Guide for Agent-Harness-RAG

> **Last Updated:** 2025-11-24
> **Framework:** LangChain Deep Agents
> **Purpose:** Harness for testing and developing Deep Agents with RAG capabilities

## Table of Contents

1. [What is Deep Agents?](#what-is-deep-agents)
2. [Repository Purpose](#repository-purpose)
3. [Core Concepts](#core-concepts)
4. [Architecture](#architecture)
5. [Middleware System](#middleware-system)
6. [Backend Storage](#backend-storage)
7. [Subagents](#subagents)
8. [RAG Integration](#rag-integration)
9. [Development Patterns](#development-patterns)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## What is Deep Agents?

**Deep Agents** is a Python library built on LangGraph that enables creation of sophisticated agents capable of handling complex, multi-step workflows. Unlike simple tool-calling loops, Deep Agents can:

- **Plan and decompose** complex tasks into manageable steps
- **Manage context** through filesystem operations to avoid token limits
- **Delegate work** to specialized subagents for task isolation
- **Persist memory** across conversations and sessions

### Core Architecture

Deep Agents differentiate from naive agents through four essential components:

1. **Detailed System Prompts** - Comprehensive instructions with examples and guidelines
2. **Planning Tool** - Task breakdown and progress tracking via todo lists
3. **Subagents** - Specialized agents for focused subtasks with context isolation
4. **File System Access** - Shared workspace for notes, memory, and collaboration

### Why Deep Agents?

Traditional agents struggle with:
- Context window overflow on complex tasks
- Loss of focus during extended reasoning
- Inability to break down sophisticated problems
- No persistent memory across sessions

Deep Agents solve these through systematic planning, context quarantine via subagents, and file-based memory management.

---

## Repository Purpose

**Agent-Harness-RAG** is a testing and development harness for Deep Agents enhanced with Retrieval-Augmented Generation (RAG) capabilities. This repository provides:

- **Testing Framework** - Evaluate Deep Agents with RAG workflows
- **Development Tools** - Build and iterate on RAG-enhanced agents
- **Benchmarks** - Measure performance of retrieval and generation
- **Examples** - Reference implementations and patterns
- **Integration Layer** - Connect Deep Agents with vector stores and embedding models

---

## Core Concepts

### The Agent Harness

The harness (deepagents) implements a core tool-calling loop with built-in capabilities:

**File System Operations:**
- `ls` - List files and directories
- `read_file` - Read file contents
- `write_file` - Write data to files
- `edit_file` - Modify existing files
- `glob` - Pattern-based file search
- `grep` - Content search across files

**Automatic Optimizations:**
- Large tool results automatically moved to files to prevent context saturation
- Old conversation history summarized when token usage exceeds limits
- Interrupted tool calls repaired to maintain message coherence
- Prompt caching reduces redundant token processing

**Task Management:**
- Todo list tracking for complex workflows
- Human-in-the-loop approval gates for destructive operations
- Progress monitoring and plan adaptation

---

## Architecture

### System Components

```
┌────────────────────────────────────────────────────────────┐
│                    Agent Harness Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Deep Agent  │  │  Planning    │  │  File System │    │
│  │  Core Loop   │  │  Middleware  │  │  Middleware  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└────────────────────────────────────────────────────────────┘
                            ↕
┌────────────────────────────────────────────────────────────┐
│                    Middleware Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  TodoList    │  │  Filesystem  │  │  SubAgent    │    │
│  │  Middleware  │  │  Middleware  │  │  Middleware  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└────────────────────────────────────────────────────────────┘
                            ↕
┌────────────────────────────────────────────────────────────┐
│                    Backend Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ StateBackend │  │ Filesystem   │  │ Store        │    │
│  │ (Ephemeral)  │  │ Backend      │  │ Backend      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└────────────────────────────────────────────────────────────┘
                            ↕
┌────────────────────────────────────────────────────────────┐
│                    RAG Layer (Custom)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Vector      │  │  Embedding   │  │  Retrieval   │    │
│  │  Store       │  │  Models      │  │  Strategies  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Query** → Deep Agent receives input
2. **Planning** → Agent creates todo list and breaks down task
3. **Retrieval** (RAG) → Query embeddings → Vector search → Document ranking
4. **Context Management** → Store retrieved docs in filesystem
5. **Subagent Delegation** → Spawn specialized agents for subtasks
6. **Generation** → LLM processes with augmented context
7. **Response** → Aggregate results and return to user

---

## Middleware System

Middleware extends agent capabilities through composable, modular components. The Deep Agents harness includes three core middleware types:

### TodoListMiddleware

**Purpose:** Enable planning and task decomposition

**Tool:** `write_todos`

**Usage:**
```python
from deepagents import create_deep_agent
from deepagents.middleware import TodoListMiddleware

agent = create_deep_agent(
    model="gpt-4",
    middleware=[TodoListMiddleware()]
)
```

**When to Use:**
- Complex, multi-part tasks requiring coordination
- Tasks where progress tracking is valuable
- Workflows that need dynamic plan adaptation

### FilesystemMiddleware

**Purpose:** Context management and persistent memory

**Tools:** `ls`, `read_file`, `write_file`, `edit_file`

**Usage:**
```python
from deepagents.middleware import FilesystemMiddleware
from deepagents.backends import StateBackend

agent = create_deep_agent(
    model="gpt-4",
    middleware=[FilesystemMiddleware(backend=StateBackend())]
)
```

**Memory Persistence:**
- Files prefixed with `/memories/` can persist across threads
- Regular files are ephemeral to the current conversation
- Use different backends for different storage requirements

**When to Use:**
- Tasks generating large intermediate outputs
- Workflows requiring information sharing between steps
- Agents needing long-term memory across sessions

### SubAgentMiddleware

**Purpose:** Task delegation and context isolation

**Tool:** `task()`

**Usage:**
```python
from deepagents.middleware import SubAgentMiddleware

# Define subagents
research_subagent = {
    "name": "research_agent",
    "description": "Research topics via web search and document analysis",
    "system_prompt": "You are a research specialist...",
    "tools": [web_search_tool, document_reader_tool]
}

agent = create_deep_agent(
    model="gpt-4",
    middleware=[SubAgentMiddleware(subagents=[research_subagent])]
)
```

**When to Use:**
✅ Multi-step tasks with large intermediate outputs
✅ Specialized domains needing custom instructions
✅ Tasks requiring different model capabilities
✅ Keeping main agent focused on high-level coordination

**When to Avoid:**
❌ Simple, single-step tasks
❌ Situations where intermediate context matters
❌ Cases where overhead exceeds benefits

### Custom Middleware

Create your own middleware by implementing the standard interface:

```python
from deepagents.middleware import BaseMiddleware

class CustomRAGMiddleware(BaseMiddleware):
    def __init__(self, vector_store, embedding_model):
        self.vector_store = vector_store
        self.embedding_model = embedding_model

    def get_tools(self):
        return [self.retrieve_documents]

    def retrieve_documents(self, query: str, k: int = 5):
        """Retrieve relevant documents from vector store."""
        embedding = self.embedding_model.embed(query)
        docs = self.vector_store.search(embedding, k=k)
        return docs
```

---

## Backend Storage

Backends are pluggable storage systems powering filesystem operations. Choose based on your persistence and deployment needs.

### StateBackend (Default)

**Purpose:** Ephemeral storage in LangGraph state

**Characteristics:**
- Files exist only for current thread
- Fast, in-memory operations
- No persistence across sessions

**Use Cases:**
- Scratch pads and temporary calculations
- Intermediate results not needed long-term
- Development and testing

**Configuration:**
```python
from deepagents.backends import StateBackend

agent = create_deep_agent(
    model="gpt-4",
    backend=StateBackend()
)
```

### FilesystemBackend

**Purpose:** Read/write to local disk

**Characteristics:**
- Actual file operations on disk
- Path sandboxing via virtual mode
- Secure symlink handling

**Use Cases:**
- Local development with real files
- CI/CD environments
- Working with existing codebases

**Configuration:**
```python
from deepagents.backends import FilesystemBackend

agent = create_deep_agent(
    model="gpt-4",
    backend=FilesystemBackend(
        root_dir="./workspace",
        virtual=True  # Sandbox paths under root_dir
    )
)
```

### StoreBackend

**Purpose:** Persist files in LangGraph Store (Redis, Postgres, etc.)

**Characteristics:**
- Cross-thread durability
- Survives across conversations
- Production deployment ready

**Use Cases:**
- Long-term agent memories
- Deployments via LangSmith
- Shared knowledge across users

**Configuration:**
```python
from deepagents.backends import StoreBackend

agent = create_deep_agent(
    model="gpt-4",
    backend=StoreBackend(
        store=my_langraph_store,
        namespace=["user", "memories"]
    )
)
```

### CompositeBackend

**Purpose:** Route different paths to different backends

**Characteristics:**
- Combine multiple backends
- Path-based routing
- Most flexible option

**Use Cases:**
- Ephemeral working files + persistent memories
- Different storage for different file types
- Complex multi-tier storage strategies

**Configuration:**
```python
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

agent = create_deep_agent(
    model="gpt-4",
    backend=CompositeBackend([
        ("/memories/", StoreBackend(store=my_store)),
        ("/", StateBackend())  # Default for all other paths
    ])
)
```

---

## Subagents

Subagents enable task delegation and context isolation. The main agent delegates work to specialized subagents, which return only final results, keeping the main agent's context clean.

### Defining Subagents

**Dictionary-based (most common):**

```python
research_agent = {
    "name": "web_researcher",
    "description": "Researches topics via web search, returns concise summaries",
    "system_prompt": """You are a web research specialist.
    Search for information, analyze results, and return concise summaries.
    Focus on factual accuracy and cite sources.""",
    "tools": [web_search, url_scraper],
    "model": "gpt-4o-mini",  # Optional: use different model
}

coding_agent = {
    "name": "code_analyzer",
    "description": "Analyzes code, finds bugs, suggests improvements",
    "system_prompt": """You are a code analysis expert.
    Review code for bugs, security issues, and performance problems.
    Provide specific, actionable recommendations.""",
    "tools": [read_file, edit_file, grep],
}
```

**CompiledSubAgent (advanced):**

```python
from deepagents import CompiledSubAgent
from langgraph.graph import StateGraph

# Build custom LangGraph
custom_graph = StateGraph(...)
# ... configure graph ...
compiled = custom_graph.compile()

subagent = CompiledSubAgent(
    name="custom_workflow",
    description="Complex workflow with custom logic",
    graph=compiled
)
```

### Using Subagents

The main agent calls subagents via the `task()` tool:

```python
# Main agent receives: "Research quantum computing and write a summary"

# Agent creates plan:
write_todos([
    "Research quantum computing via web_researcher subagent",
    "Write comprehensive summary from research",
    "Save summary to file"
])

# Agent delegates to subagent:
research_result = task(
    subagent="web_researcher",
    task="Research quantum computing: key concepts, recent advances, applications"
)

# Main agent receives only the final summary, not all intermediate tool calls
```

### Subagent Best Practices

1. **Clear Descriptions:** Write specific descriptions so main agent knows when to delegate
2. **Focused System Prompts:** Provide detailed instructions with examples
3. **Minimal Tool Sets:** Only include tools needed for the subagent's purpose
4. **Concise Outputs:** Return summaries, not raw data, to keep context clean
5. **Error Handling:** Handle failures gracefully and report back to main agent

### When to Use Subagents

✅ **Good use cases:**
- Web research with many search results
- File operations across multiple files
- Specialized analysis requiring domain expertise
- Tasks with different model requirements (e.g., fast model for simple tasks)

❌ **Avoid for:**
- Single tool calls
- Simple operations
- When intermediate steps are important to main agent
- Overhead cost exceeds benefits

---

## RAG Integration

This harness extends Deep Agents with Retrieval-Augmented Generation capabilities. RAG enhances agents by retrieving relevant documents before generation.

### RAG Architecture

```python
from deepagents import create_deep_agent
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

# Initialize RAG components
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(
    collection_name="knowledge_base",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# Create RAG tool for agent
def retrieve_knowledge(query: str, k: int = 5) -> str:
    """Retrieve relevant documents from knowledge base."""
    docs = vectorstore.similarity_search(query, k=k)

    # Write docs to file for agent to read
    context = "\n\n---\n\n".join([
        f"Document {i+1}:\n{doc.page_content}"
        for i, doc in enumerate(docs)
    ])

    return f"Retrieved {len(docs)} relevant documents. Use read_file to review them."

# Create agent with RAG capability
agent = create_deep_agent(
    model="gpt-4",
    tools=[retrieve_knowledge],
    system_prompt="""You are a research assistant with access to a knowledge base.
    When answering questions:
    1. Use retrieve_knowledge to find relevant documents
    2. Read and analyze the retrieved documents
    3. Synthesize information into a comprehensive answer
    4. Cite sources when appropriate"""
)
```

### RAG Workflow

1. **Query Understanding** - Agent analyzes user question
2. **Retrieval Planning** - Decides what to retrieve and how
3. **Vector Search** - Generate embeddings and search vector store
4. **Document Storage** - Save retrieved docs to filesystem
5. **Context Analysis** - Read and process relevant documents
6. **Response Generation** - Synthesize information with LLM
7. **Citation** - Reference sources in final answer

### RAG Subagent Pattern

Create a specialized RAG subagent for complex retrieval:

```python
rag_subagent = {
    "name": "rag_researcher",
    "description": "Retrieves and analyzes documents from knowledge base",
    "system_prompt": """You are a RAG specialist.
    1. Retrieve documents relevant to the query
    2. Analyze documents for key information
    3. Return a structured summary with citations""",
    "tools": [retrieve_knowledge, read_file, write_file]
}

# Main agent delegates RAG work to subagent
agent = create_deep_agent(
    model="gpt-4",
    middleware=[SubAgentMiddleware(subagents=[rag_subagent])]
)
```

### Hybrid RAG Strategies

Combine multiple retrieval methods:

```python
def hybrid_retrieve(query: str, k: int = 5):
    """Hybrid retrieval using dense and sparse methods."""

    # Dense retrieval (vector similarity)
    dense_results = vectorstore.similarity_search(query, k=k)

    # Sparse retrieval (BM25/keyword)
    sparse_results = bm25_search(query, k=k)

    # Rerank combined results
    combined = rerank(dense_results + sparse_results, query)

    return combined[:k]
```

---

## Development Patterns

### Pattern 1: Complex Research Task

```python
from deepagents import create_deep_agent

# Define research subagent
research_subagent = {
    "name": "researcher",
    "description": "Conducts deep research on topics via web and documents",
    "system_prompt": """Research specialist. Search web, read documents,
    analyze information, return comprehensive summaries with sources.""",
    "tools": [web_search, retrieve_knowledge, read_file, write_file]
}

# Main coordinator agent
agent = create_deep_agent(
    model="gpt-4",
    middleware=[
        TodoListMiddleware(),
        FilesystemMiddleware(),
        SubAgentMiddleware(subagents=[research_subagent])
    ],
    system_prompt="""You are a research coordinator.
    Break down complex research tasks, delegate to researcher subagent,
    synthesize findings, and produce final reports."""
)

# Usage
response = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Research the state of quantum computing in 2024"
    }]
})
```

### Pattern 2: Document Analysis Pipeline

```python
# Analysis subagent
analysis_subagent = {
    "name": "analyzer",
    "description": "Analyzes documents for specific information",
    "system_prompt": """Document analyst. Extract key information,
    identify patterns, summarize findings.""",
    "tools": [read_file, grep, write_file]
}

# Create agent with file and subagent support
agent = create_deep_agent(
    model="gpt-4",
    backend=FilesystemBackend(root_dir="./documents"),
    middleware=[SubAgentMiddleware(subagents=[analysis_subagent])]
)

# Agent can now:
# 1. List documents with ls
# 2. Delegate analysis to subagent
# 3. Aggregate results
# 4. Write final report
```

### Pattern 3: Multi-Stage RAG

```python
# Stage 1: Broad retrieval
def initial_retrieve(query: str) -> List[str]:
    """Cast wide net for potentially relevant docs."""
    return vectorstore.similarity_search(query, k=20)

# Stage 2: Focused retrieval via subagent
rag_subagent = {
    "name": "rag_filter",
    "description": "Filters and ranks retrieved documents by relevance",
    "system_prompt": """Review documents and select most relevant.
    Score each document's relevance to the query.""",
    "tools": [read_file, write_file]
}

# Main agent orchestrates multi-stage RAG
agent = create_deep_agent(
    model="gpt-4",
    tools=[initial_retrieve],
    middleware=[SubAgentMiddleware(subagents=[rag_subagent])]
)
```

### Pattern 4: Persistent Memory

```python
# Use CompositeBackend for memories
agent = create_deep_agent(
    model="gpt-4",
    backend=CompositeBackend([
        ("/memories/", StoreBackend(store=persistent_store)),
        ("/", StateBackend())
    ]),
    system_prompt="""You have access to long-term memories in /memories/.
    Save important information there for future conversations.
    Use regular files for temporary work."""
)

# Agent can now:
# - Save: write_file("/memories/user_preferences.txt", data)
# - Recall: read_file("/memories/user_preferences.txt")
# - Memories persist across sessions
```

---

## Best Practices

### Planning and Decomposition

✅ **Do:**
- Break complex tasks into discrete, manageable steps
- Use `write_todos` tool early in complex workflows
- Update todos as you progress and learn more
- Keep todo items actionable and specific

❌ **Don't:**
- Skip planning for multi-step tasks
- Create vague or ambiguous todo items
- Forget to update completed todos

```python
# Good todo list
write_todos([
    "Retrieve relevant documents about quantum computing",
    "Analyze documents and extract key concepts",
    "Research recent advances via web search",
    "Synthesize findings into comprehensive summary",
    "Save summary to /memories/quantum_research.md"
])

# Bad todo list (too vague)
write_todos([
    "Do research",
    "Write stuff",
    "Finish"
])
```

### Context Management

✅ **Do:**
- Use files for large outputs instead of keeping in messages
- Write intermediate results to files for later reference
- Use descriptive filenames with context
- Clean up temporary files when done

❌ **Don't:**
- Keep large tool outputs in conversation context
- Create hundreds of small files (use consolidation)
- Use cryptic filenames

```python
# Good: Save large output to file
search_results = web_search("quantum computing")
write_file("/workspace/search_results.txt", search_results)
write_todos([
    "✓ Completed web search, saved to /workspace/search_results.txt",
    "Analyze search results and extract key papers"
])

# Bad: Keep large output in context
# This bloats context window unnecessarily
```

### Subagent Delegation

✅ **Do:**
- Delegate when subtasks have large intermediate outputs
- Use specialized subagents for domain-specific work
- Write clear task descriptions for subagents
- Keep subagent tool sets minimal and focused

❌ **Don't:**
- Delegate trivial single-tool operations
- Create subagents with too many tools
- Expect subagent to maintain state with main agent

```python
# Good: Delegate complex research
task(
    subagent="web_researcher",
    task="""Research quantum computing error correction.
    Find: 1) recent papers, 2) key techniques, 3) current challenges.
    Return structured summary with citations."""
)

# Bad: Delegate simple operation
task(subagent="reader", task="Read file.txt")  # Just use read_file!
```

### RAG Optimization

✅ **Do:**
- Retrieve documents before generating answers
- Store retrieved docs in files for analysis
- Use appropriate k value (typically 3-10)
- Rerank results when needed for quality
- Cite sources in your responses

❌ **Don't:**
- Generate answers without retrieval
- Retrieve too many documents (context overflow)
- Retrieve too few documents (miss information)
- Forget to cite sources

```python
# Good: Structured RAG workflow
def answer_with_rag(query: str):
    # 1. Retrieve
    docs = retrieve_knowledge(query, k=5)
    write_file("/workspace/retrieved_docs.txt", docs)

    # 2. Analyze
    analysis = task(
        subagent="analyzer",
        task=f"Analyze /workspace/retrieved_docs.txt for: {query}"
    )

    # 3. Generate with citations
    return generate_answer_with_sources(analysis)
```

### Error Handling

✅ **Do:**
- Check if files exist before reading
- Handle missing or malformed data gracefully
- Retry failed operations with backoff
- Log errors for debugging
- Provide helpful error messages

❌ **Don't:**
- Assume operations always succeed
- Crash on first error
- Silently swallow exceptions
- Leave partial state on errors

```python
# Good: Robust file operations
try:
    if ls().contains("data.txt"):
        content = read_file("data.txt")
    else:
        content = "Default content"
except Exception as e:
    write_file("/logs/error.txt", f"Error reading data: {e}")
    content = fallback_content()
```

### Performance Optimization

✅ **Do:**
- Use prompt caching for repeated prompts
- Cache embeddings for frequent queries
- Batch operations when possible
- Use faster models for simple subtasks
- Monitor token usage

❌ **Don't:**
- Regenerate embeddings unnecessarily
- Use slow models for trivial operations
- Make redundant API calls
- Ignore context window limits

```python
# Good: Use appropriate models per task
main_agent = create_deep_agent(
    model="gpt-4",  # Complex reasoning
    middleware=[SubAgentMiddleware(subagents=[
        {
            "name": "simple_tasks",
            "description": "Handles simple, routine tasks",
            "model": "gpt-4o-mini",  # Faster, cheaper
            "tools": [read_file, write_file]
        }
    ])]
)
```

---

## Troubleshooting

### Issue: Context Window Overflow

**Symptoms:** Errors about token limits, truncated responses

**Solutions:**
- Use filesystem to store large outputs instead of messages
- Delegate large operations to subagents
- Enable automatic summarization in harness
- Reduce retrieval k value

```python
# Bad: Keep everything in context
results = [tool1(), tool2(), tool3()]  # Each returns 5000 tokens

# Good: Use files
write_file("/workspace/results1.txt", tool1())
write_file("/workspace/results2.txt", tool2())
write_file("/workspace/results3.txt", tool3())
```

### Issue: Poor Retrieval Quality

**Symptoms:** Retrieved documents not relevant, incorrect answers

**Solutions:**
- Check embedding model compatibility
- Tune similarity threshold
- Try hybrid retrieval (dense + sparse)
- Implement reranking
- Verify document chunking strategy

```python
# Add reranking
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker

reranker = CrossEncoderReranker(model_name="cross-encoder/ms-marco-MiniLM-L-12-v2")
compression_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=vectorstore.as_retriever()
)
```

### Issue: Subagent Not Being Called

**Symptoms:** Main agent does work itself instead of delegating

**Solutions:**
- Make subagent description more specific
- Improve main agent's system prompt
- Verify subagent name matches
- Check if task complexity warrants delegation

```python
# Bad description (too vague)
subagent = {
    "name": "helper",
    "description": "Helps with stuff",
    ...
}

# Good description (specific)
subagent = {
    "name": "web_researcher",
    "description": "Use for web searches requiring >3 queries or analyzing >10 URLs",
    ...
}
```

### Issue: Slow Performance

**Symptoms:** Long response times, timeouts

**Solutions:**
- Use faster models for subagents (gpt-4o-mini)
- Enable prompt caching
- Reduce number of tool calls
- Optimize retrieval (lower k)
- Batch operations

```python
# Enable caching in LangGraph
agent = create_deep_agent(
    model="gpt-4",
    cache_prompt=True  # Reuse system prompt
)
```

### Issue: Memory Not Persisting

**Symptoms:** Agent forgets information across conversations

**Solutions:**
- Use StoreBackend for persistent storage
- Save to `/memories/` path with CompositeBackend
- Verify store connection
- Check namespace configuration

```python
# Ensure persistence
agent = create_deep_agent(
    model="gpt-4",
    backend=CompositeBackend([
        ("/memories/", StoreBackend(store=redis_store)),  # Persistent
        ("/", StateBackend())  # Ephemeral
    ])
)

# Save important info
write_file("/memories/user_info.txt", data)  # Persists
write_file("/workspace/temp.txt", data)  # Ephemeral
```

### Issue: File Operations Failing

**Symptoms:** Cannot read/write files, permission errors

**Solutions:**
- Check backend configuration
- Verify root_dir exists (FilesystemBackend)
- Use virtual mode for sandboxing
- Check file paths (absolute vs relative)

```python
# Safe filesystem backend
agent = create_deep_agent(
    model="gpt-4",
    backend=FilesystemBackend(
        root_dir="./workspace",
        virtual=True,  # Sandbox under root_dir
        create_root=True  # Auto-create if missing
    )
)
```

---

## Additional Resources

### LangChain Deep Agents Documentation

- **Overview:** https://docs.langchain.com/oss/python/deepagents/overview
- **Harness:** https://docs.langchain.com/oss/python/deepagents/harness
- **Middleware:** https://docs.langchain.com/oss/python/deepagents/middleware
- **Backends:** https://docs.langchain.com/oss/python/deepagents/backends
- **Subagents:** https://docs.langchain.com/oss/python/deepagents/subagents
- **Blog Post:** https://blog.langchain.com/deep-agents/

### Related Technologies

- **LangGraph:** https://langchain-ai.github.io/langgraph/
- **LangChain:** https://python.langchain.com/
- **LangSmith:** https://smith.langchain.com/
- **Vector Stores:** https://python.langchain.com/docs/modules/data_connection/vectorstores/

### RAG Resources

- **RAG Paper:** https://arxiv.org/abs/2005.11401
- **LangChain RAG Guide:** https://python.langchain.com/docs/use_cases/question_answering/
- **Embeddings Leaderboard:** https://huggingface.co/spaces/mteb/leaderboard
- **Vector DB Comparison:** https://github.com/erikbern/ann-benchmarks

---

## Quick Start Example

```python
from deepagents import create_deep_agent
from deepagents.middleware import TodoListMiddleware, FilesystemMiddleware, SubAgentMiddleware
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

# Initialize RAG components
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(embedding_function=embeddings)

# Define RAG tool
def retrieve_docs(query: str, k: int = 5) -> str:
    docs = vectorstore.similarity_search(query, k=k)
    return "\n\n".join([doc.page_content for doc in docs])

# Define specialized subagent
research_subagent = {
    "name": "researcher",
    "description": "Researches topics via document retrieval and analysis",
    "system_prompt": "You are a research specialist. Retrieve and analyze documents.",
    "tools": [retrieve_docs, read_file, write_file]
}

# Create Deep Agent with RAG
agent = create_deep_agent(
    model="gpt-4",
    tools=[retrieve_docs],
    backend=CompositeBackend([
        ("/memories/", StoreBackend(store=my_store)),
        ("/", StateBackend())
    ]),
    middleware=[
        TodoListMiddleware(),
        FilesystemMiddleware(),
        SubAgentMiddleware(subagents=[research_subagent])
    ],
    system_prompt="""You are a RAG-enhanced research assistant.
    Use retrieve_docs to find relevant information.
    Delegate complex research to the researcher subagent.
    Save important findings to /memories/ for future reference."""
)

# Run agent
response = agent.invoke({
    "messages": [{"role": "user", "content": "What is quantum entanglement?"}]
})
```

---

**Note for AI Assistants:** This repository implements a harness for LangChain Deep Agents with RAG capabilities. When working with this codebase:

1. **Understand Deep Agents architecture** - Planning, filesystem, subagents are core
2. **Use middleware appropriately** - TodoList for planning, Filesystem for context, SubAgent for delegation
3. **Choose correct backend** - StateBackend for ephemeral, StoreBackend for persistent
4. **Integrate RAG thoughtfully** - Retrieval before generation, store docs in files
5. **Follow best practices** - Context management, appropriate delegation, error handling
6. **Reference documentation** - Official LangChain Deep Agents docs are authoritative

This framework enables sophisticated, long-running agent workflows with proper context management and task decomposition.
