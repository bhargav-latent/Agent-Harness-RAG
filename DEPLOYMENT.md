# LangGraph Deployment & Testing Guide

> **How to deploy agents with LangGraph CLI and test both RAG approaches side-by-side**

## Overview

This guide shows how to:
1. Deploy FileSearch and Vector Store RAG agents using LangGraph CLI
2. Access both agents in separate browser tabs
3. Test with the same question to compare responses
4. Capture and analyze results side-by-side

---

## Prerequisites

### Install LangGraph CLI

```bash
# Install LangGraph CLI
pip install langgraph-cli

# Verify installation
langgraph --version
```

### Install Dependencies

```bash
# Core dependencies
pip install langchain langgraph langchain-openai

# For Vector Store RAG
pip install chromadb sentence-transformers

# For local models
pip install openai  # For API-compatible endpoints
```

---

## Project Structure

```
Agent-Harness-RAG/
├── agents/
│   ├── filesearch_agent.py      # FileSearch RAG implementation
│   └── vectorstore_agent.py     # Vector Store RAG implementation
├── langgraph.json               # LangGraph CLI configuration
├── .env                         # Environment variables
└── documents/                   # Document corpus
```

---

## Step 1: Create LangGraph Configuration

Create `langgraph.json` in project root:

```json
{
  "dependencies": [
    "langchain",
    "langgraph",
    "langchain-openai",
    "chromadb",
    "sentence-transformers"
  ],
  "graphs": {
    "filesearch_agent": {
      "path": "agents/filesearch_agent.py:graph",
      "description": "FileSearch RAG using grep/glob tools"
    },
    "vectorstore_agent": {
      "path": "agents/vectorstore_agent.py:graph",
      "description": "Vector Store RAG using ChromaDB and reranking"
    }
  },
  "env": ".env"
}
```

---

## Step 2: Implement Agents

### FileSearch Agent (`agents/filesearch_agent.py`)

```python
from langgraph.graph import StateGraph, MessagesState
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from deepagents.middleware import TodoListMiddleware, FilesystemMiddleware
from deepagents.backends import FilesystemBackend

# Initialize LLM
llm = ChatOpenAI(
    base_url=os.getenv("LLM_BASE_URL"),
    model=os.getenv("LLM_MODEL"),
    temperature=float(os.getenv("LLM_TEMPERATURE", 0.7)),
    max_tokens=int(os.getenv("LLM_MAX_TOKENS", 8192))
)

# Create FileSearch agent
agent = create_deep_agent(
    model=llm,
    backend=FilesystemBackend(root_dir="./documents"),
    middleware=[
        TodoListMiddleware(),
        FilesystemMiddleware()
    ],
    system_prompt="""You are a FileSearch RAG assistant.
    Use grep and glob to search documents, then read_file to extract content.
    Answer questions with citations from the documents."""
)

# Export as LangGraph
graph = agent.compile()
```

### Vector Store Agent (`agents/vectorstore_agent.py`)

```python
from langgraph.graph import StateGraph, MessagesState
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker
from deepagents import create_deep_agent
from deepagents.middleware import TodoListMiddleware
import os

# Initialize components
llm = ChatOpenAI(
    base_url=os.getenv("LLM_BASE_URL"),
    model=os.getenv("LLM_MODEL"),
    temperature=float(os.getenv("LLM_TEMPERATURE", 0.7)),
    max_tokens=int(os.getenv("LLM_MAX_TOKENS", 8192))
)

embeddings = OpenAIEmbeddings(
    base_url=os.getenv("EMBEDDINGS_BASE_URL"),
    model=os.getenv("EMBEDDINGS_MODEL")
)

# Initialize ChromaDB
vectorstore = Chroma(
    collection_name="documents",
    embedding_function=embeddings,
    persist_directory=os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
)

# Initialize reranker (local)
cross_encoder = HuggingFaceCrossEncoder(
    model_name=os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-base")
)
compressor = CrossEncoderReranker(
    model=cross_encoder,
    top_n=int(os.getenv("RERANK_TOP_N", 5))
)

# Create retriever with reranking
base_retriever = vectorstore.as_retriever(
    search_kwargs={"k": int(os.getenv("INITIAL_K", 20))}
)
retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever
)

# Create RAG tool
def retrieve_and_answer(query: str) -> str:
    """Retrieve relevant documents and generate answer."""
    docs = retriever.get_relevant_documents(query)
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""Context from documents:
{context}

Question: {query}

Answer based on the context provided, with citations."""

    return llm.predict(prompt)

# Create Vector Store agent
agent = create_deep_agent(
    model=llm,
    tools=[retrieve_and_answer],
    middleware=[TodoListMiddleware()],
    system_prompt="""You are a Vector Store RAG assistant.
    Use retrieve_and_answer to search documents semantically.
    Answer questions with citations from retrieved context."""
)

# Export as LangGraph
graph = agent.compile()
```

---

## Step 3: Start LangGraph Development Server

### Start Both Agents

```bash
# Navigate to project directory
cd Agent-Harness-RAG

# Start LangGraph dev server
langgraph dev

# Server will start on http://localhost:8123
```

**Output:**
```
🚀 LangGraph Dev Server starting...
📦 Loading graphs from langgraph.json
✅ Loaded: filesearch_agent
✅ Loaded: vectorstore_agent
🌐 Server running at http://localhost:8123
📊 Studio UI: http://localhost:8123/studio
```

---

## Step 4: Access LangGraph Studio UI

### Open in Browser

1. **Open first browser tab:**
   ```
   http://localhost:8123/studio?thread=filesearch_test&graph=filesearch_agent
   ```

2. **Open second browser tab:**
   ```
   http://localhost:8123/studio?thread=vectorstore_test&graph=vectorstore_agent
   ```

### URL Parameters Explained

- `thread=<name>` - Unique conversation thread ID
- `graph=<agent_name>` - Which agent to load (from langgraph.json)

---

## Step 5: Side-by-Side Testing

### Testing Workflow

1. **Arrange Windows:**
   - Split screen or use dual monitors
   - Left: FileSearch agent tab
   - Right: Vector Store agent tab

2. **Ask Same Question in Both:**

   **Example Question:**
   ```
   What is the attention mechanism in the transformer architecture?
   ```

3. **Send to Both Agents:**
   - Type question in FileSearch tab → Send
   - Copy same question to Vector Store tab → Send

4. **Compare Responses:**
   - FileSearch: Shows grep/glob searches, file reads
   - Vector Store: Shows vector search, reranking

### Screenshot Setup

**Browser Layout:**
```
┌─────────────────────────┬─────────────────────────┐
│  FileSearch RAG         │  Vector Store RAG       │
│  (Tab 1)                │  (Tab 2)                │
│                         │                         │
│  Question: What is...   │  Question: What is...   │
│                         │                         │
│  Response:              │  Response:              │
│  Using grep to search.. │  Searching vector db... │
│  Found in attention_... │  Retrieved 5 docs...    │
│  ...                    │  ...                    │
└─────────────────────────┴─────────────────────────┘
```

---

## Step 6: Capture and Compare

### Taking Screenshots

**Using Built-in Tools:**

**macOS:**
```bash
# Full screen
Cmd + Shift + 3

# Selected area
Cmd + Shift + 4
```

**Windows:**
```bash
# Snipping Tool
Windows Key + Shift + S
```

**Linux:**
```bash
# GNOME Screenshot
gnome-screenshot -a
```

### Organize Screenshots

```
evaluation/screenshots/
├── filesearch_question1.png
├── vectorstore_question1.png
├── filesearch_question2.png
├── vectorstore_question2.png
└── comparison_sidebyside.png
```

---

## Step 7: Recording Metrics

### LangGraph Studio Features

**Built-in Metrics:**
- **Response time** - Shown in UI
- **Token usage** - Displayed per message
- **Tool calls** - Listed with timing

**Accessing Metrics:**
```
1. Look at bottom of chat for "Stats" section
2. Token count: Input/Output tokens
3. Latency: Time from send to response
4. Tools: Which tools were called
```

### Manual Recording

Create a comparison table:

```markdown
| Question | Agent | Correctness | Latency | Tokens | Cost |
|----------|-------|-------------|---------|--------|------|
| Q1: Attention mechanism | FileSearch | ✅ | 2.3s | 856 | $0.05 |
| Q1: Attention mechanism | VectorStore | ✅ | 4.1s | 1243 | $0.08 |
```

---

## Step 8: Advanced Testing

### Using Multiple Threads

Test multiple questions simultaneously:

```bash
# FileSearch - Question 1
http://localhost:8123/studio?thread=fs_q1&graph=filesearch_agent

# FileSearch - Question 2
http://localhost:8123/studio?thread=fs_q2&graph=filesearch_agent

# Vector Store - Question 1
http://localhost:8123/studio?thread=vs_q1&graph=vectorstore_agent

# Vector Store - Question 2
http://localhost:8123/studio?thread=vs_q2&graph=vectorstore_agent
```

### Batch Testing

Create a test script:

```python
import requests
import json

API_URL = "http://localhost:8123"

questions = [
    "What is the attention mechanism?",
    "Explain multi-head attention",
    "How does positional encoding work?"
]

def test_agent(agent_name, questions):
    results = []
    for i, q in enumerate(questions):
        response = requests.post(
            f"{API_URL}/runs",
            json={
                "graph": agent_name,
                "thread_id": f"{agent_name}_q{i}",
                "input": {"messages": [{"role": "user", "content": q}]}
            }
        )
        results.append(response.json())
    return results

# Test both agents
filesearch_results = test_agent("filesearch_agent", questions)
vectorstore_results = test_agent("vectorstore_agent", questions)
```

---

## Step 9: Using LangSmith for Monitoring (Optional)

### Enable LangSmith Tracing

```bash
# Add to .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key_here
LANGCHAIN_PROJECT=agent-harness-rag
```

### Benefits
- See full execution traces
- Compare agent runs side-by-side
- Track performance over time
- Debug tool calls and reasoning

**Access:** https://smith.langchain.com

---

## Common Issues & Solutions

### Issue: Port Already in Use

```bash
# Kill process on port 8123
lsof -ti:8123 | xargs kill -9

# Or specify different port
langgraph dev --port 8124
```

### Issue: Agent Not Loading

**Check langgraph.json:**
- Correct path to agent files
- Graph exported correctly
- All dependencies installed

**Verify:**
```bash
python -c "from agents.filesearch_agent import graph; print('OK')"
```

### Issue: Environment Variables Not Loading

**Ensure .env in project root:**
```bash
# Check .env is loaded
langgraph dev --print-env
```

### Issue: ChromaDB Not Found (Vector Store)

**Initialize ChromaDB first:**
```bash
python scripts/initialize_vectorstore.py
```

---

## Testing Checklist

Before comparison testing:

- [ ] Both agents deployed via LangGraph CLI
- [ ] Server running on http://localhost:8123
- [ ] FileSearch tab open with unique thread ID
- [ ] Vector Store tab open with unique thread ID
- [ ] Same test question prepared
- [ ] Screenshot tool ready
- [ ] Metrics recording sheet prepared
- [ ] Document corpus available in documents/

---

## Example Testing Session

### Session Plan

**Date:** 2025-11-24
**Questions:** 5 from different categories
**Agents:** FileSearch vs Vector Store
**Metrics:** Correctness, Latency, Token Usage

### Test Questions

1. **Exact Match:** "What is the formula for scaled dot-product attention?"
2. **Semantic:** "How does the transformer handle sequence ordering?"
3. **Multi-hop:** "Explain how self-attention and multi-head attention work together"
4. **Conceptual:** "Why is attention more effective than RNNs for long sequences?"
5. **Table Data:** "What are the model configurations in the transformer paper?"

### Recording Template

```
Question: [Question text]

FileSearch Agent:
- Response: [Copy response]
- Correctness: [ ] Correct [ ] Incorrect
- Latency: [X.X seconds]
- Tokens: [Input: XXX, Output: XXX]
- Tools Used: [grep, glob, read_file, etc.]
- Notes: [Any observations]

Vector Store Agent:
- Response: [Copy response]
- Correctness: [ ] Correct [ ] Incorrect
- Latency: [X.X seconds]
- Tokens: [Input: XXX, Output: XXX]
- Tools Used: [retrieve_and_answer, etc.]
- Notes: [Any observations]

Winner: [ ] FileSearch [ ] VectorStore [ ] Tie
Reason: [Brief explanation]
```

---

## Screenshot Best Practices

### What to Capture

1. **Full UI** - Show entire chat interface
2. **Question Input** - Clearly visible question
3. **Response** - Complete agent response
4. **Metrics** - Token count, latency at bottom
5. **Tool Calls** - Expandable tool call section

### Annotation

Use screenshot annotation tools to:
- Highlight key differences
- Circle metrics
- Add arrows pointing to important parts
- Add text labels for comparison

### Organization

```
screenshots/
├── comparison_1_attention_mechanism.png
├── comparison_2_positional_encoding.png
├── comparison_3_multi_head.png
├── filesearch_detailed_q1.png
├── vectorstore_detailed_q1.png
└── metrics_summary.png
```

---

## Advanced: Automated Testing

### Using LangGraph API

```python
import requests
import time
from typing import List, Dict

class AgentTester:
    def __init__(self, base_url: str = "http://localhost:8123"):
        self.base_url = base_url

    def test_question(self, graph: str, question: str, thread_id: str) -> Dict:
        """Test a single question on specified agent."""
        start_time = time.time()

        response = requests.post(
            f"{self.base_url}/runs",
            json={
                "graph": graph,
                "thread_id": thread_id,
                "input": {"messages": [{"role": "user", "content": question}]}
            }
        )

        latency = time.time() - start_time
        result = response.json()

        return {
            "question": question,
            "agent": graph,
            "response": result.get("output"),
            "latency": latency,
            "tokens": result.get("usage", {}),
            "thread_id": thread_id
        }

    def compare_agents(self, questions: List[str]) -> List[Dict]:
        """Compare FileSearch and Vector Store on same questions."""
        results = []

        for i, q in enumerate(questions):
            # Test FileSearch
            fs_result = self.test_question(
                graph="filesearch_agent",
                question=q,
                thread_id=f"fs_test_{i}"
            )
            results.append(fs_result)

            # Test Vector Store
            vs_result = self.test_question(
                graph="vectorstore_agent",
                question=q,
                thread_id=f"vs_test_{i}"
            )
            results.append(vs_result)

        return results

# Usage
tester = AgentTester()
questions = [
    "What is the attention mechanism?",
    "Explain positional encoding"
]
results = tester.compare_agents(questions)

# Save results
import json
with open("test_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

---

## Summary

### Deployment Steps
1. Create `langgraph.json` config
2. Implement both agents
3. Run `langgraph dev`
4. Access Studio UI in browser

### Testing Steps
1. Open two tabs with different agents
2. Ask same question in both
3. Compare responses side-by-side
4. Record metrics (Correctness, Latency, Cost)
5. Take screenshots for documentation

### Key URLs
- **Dev Server:** http://localhost:8123
- **Studio UI:** http://localhost:8123/studio
- **FileSearch:** http://localhost:8123/studio?thread=fs&graph=filesearch_agent
- **Vector Store:** http://localhost:8123/studio?thread=vs&graph=vectorstore_agent

---

## References

- [LangGraph CLI Documentation](https://langchain-ai.github.io/langgraph/cloud/reference/cli/)
- [LangGraph Studio Guide](https://langchain-ai.github.io/langgraph/cloud/quick_start/)
- [Deep Agents Deployment](https://docs.langchain.com/oss/python/deepagents/deployment)
- [LangSmith Tracing](https://smith.langchain.com/)

---

**Ready to deploy and test both agents side-by-side!** 🚀
