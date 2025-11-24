# CLAUDE.md - AI Assistant Guide for Agent-Harness-RAG

> **Last Updated:** 2025-11-24
> **Repository:** Agent-Harness-RAG
> **Purpose:** Testing and evaluation framework for AI agents with RAG capabilities

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Codebase Structure](#codebase-structure)
4. [Development Workflows](#development-workflows)
5. [Key Conventions](#key-conventions)
6. [RAG Components](#rag-components)
7. [Testing & Validation](#testing--validation)
8. [Common Tasks](#common-tasks)
9. [Troubleshooting](#troubleshooting)

---

## Project Overview

**Agent-Harness-RAG** is a comprehensive testing and evaluation framework designed for AI agents that utilize Retrieval-Augmented Generation (RAG) capabilities. This harness provides:

- **Standardized Testing Environment**: Consistent evaluation across different agent implementations
- **RAG Integration**: Built-in support for document retrieval and context augmentation
- **Performance Metrics**: Tools for measuring agent accuracy, latency, and resource usage
- **Extensible Architecture**: Easy integration of new agents, retrievers, and data sources

### Key Technologies

- Python-based agent framework
- Vector databases for document retrieval
- Embedding models for semantic search
- Evaluation metrics and benchmarking tools
- Integration with LLM providers

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent Harness Layer                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Agent      │  │   Retriever  │  │  Evaluator   │      │
│  │  Interface   │  │   Manager    │  │   Engine     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
├─────────────────────────────────────────────────────────────┤
│                      RAG Components                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Vector     │  │  Embedding   │  │  Document    │      │
│  │   Store      │  │   Models     │  │  Processor   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
├─────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                      │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Query Input** → Agent receives user query
2. **Retrieval** → Embedding generation → Vector search → Document ranking
3. **Augmentation** → Context construction from retrieved documents
4. **Generation** → LLM processes augmented prompt
5. **Evaluation** → Metrics collection and validation
6. **Response** → Output formatting and delivery

---

## Codebase Structure

### Expected Directory Layout

```
Agent-Harness-RAG/
├── src/                          # Source code
│   ├── agents/                   # Agent implementations
│   │   ├── base_agent.py        # Abstract base class
│   │   ├── rag_agent.py         # RAG-enabled agent
│   │   └── custom_agents/       # Custom agent implementations
│   ├── retrievers/               # Document retrieval
│   │   ├── vector_retriever.py  # Vector-based retrieval
│   │   ├── hybrid_retriever.py  # Hybrid search
│   │   └── reranker.py          # Result re-ranking
│   ├── embeddings/               # Embedding models
│   │   ├── model_loader.py      # Model initialization
│   │   └── batch_encoder.py     # Batch processing
│   ├── vectorstore/              # Vector database integrations
│   │   ├── base_store.py        # Abstract interface
│   │   ├── chroma_store.py      # ChromaDB
│   │   ├── pinecone_store.py    # Pinecone
│   │   └── qdrant_store.py      # Qdrant
│   ├── evaluation/               # Testing and metrics
│   │   ├── metrics.py           # Performance metrics
│   │   ├── benchmarks.py        # Benchmark suites
│   │   └── validators.py        # Output validation
│   ├── utils/                    # Utilities
│   │   ├── config.py            # Configuration management
│   │   ├── logging.py           # Logging setup
│   │   └── helpers.py           # Helper functions
│   └── harness.py               # Main harness orchestrator
├── tests/                        # Test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── fixtures/                # Test data and fixtures
├── data/                         # Data directory
│   ├── documents/               # Source documents
│   ├── queries/                 # Test queries
│   └── ground_truth/            # Evaluation datasets
├── configs/                      # Configuration files
│   ├── agents/                  # Agent configs
│   ├── retrievers/              # Retriever configs
│   └── evaluation/              # Evaluation configs
├── scripts/                      # Utility scripts
│   ├── setup.sh                 # Environment setup
│   ├── ingest_documents.py      # Document ingestion
│   └── run_benchmark.py         # Benchmark execution
├── docs/                         # Documentation
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project configuration
├── .env.example                 # Environment variables template
└── README.md                    # Project documentation
```

---

## Development Workflows

### Setting Up Development Environment

```bash
# Clone repository
git clone <repository-url>
cd Agent-Harness-RAG

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configurations

# Run initial setup
python scripts/setup.py
```

### Adding a New Agent

1. **Create agent class** in `src/agents/custom_agents/`
2. **Inherit from** `BaseAgent` or `RAGAgent`
3. **Implement required methods**:
   - `initialize()`
   - `process_query(query: str) -> str`
   - `cleanup()`
4. **Register agent** in agent registry
5. **Add configuration** in `configs/agents/`
6. **Write tests** in `tests/unit/agents/`

### Adding a New Retriever

1. **Create retriever class** in `src/retrievers/`
2. **Inherit from** `BaseRetriever`
3. **Implement methods**:
   - `retrieve(query: str, k: int) -> List[Document]`
   - `add_documents(documents: List[Document])`
4. **Add configuration** in `configs/retrievers/`
5. **Write integration tests**

### Running Tests

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_rag_agent.py -v
```

### Running Benchmarks

```bash
# Run full benchmark suite
python scripts/run_benchmark.py

# Run specific benchmark
python scripts/run_benchmark.py --benchmark retrieval_accuracy

# Run with custom config
python scripts/run_benchmark.py --config configs/evaluation/custom_benchmark.yaml
```

---

## Key Conventions

### Code Style

- **Language**: Python 3.9+
- **Formatting**: Black (line length: 88)
- **Linting**: Ruff or Flake8
- **Type Hints**: Required for all public methods
- **Docstrings**: Google style docstrings

### Naming Conventions

- **Classes**: PascalCase (e.g., `RAGAgent`, `VectorRetriever`)
- **Functions**: snake_case (e.g., `process_query`, `load_documents`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`, `DEFAULT_K`)
- **Private methods**: Prefix with underscore (e.g., `_internal_method`)

### Import Organization

```python
# Standard library
import os
from typing import List, Dict, Optional

# Third-party
import numpy as np
from langchain.embeddings import OpenAIEmbeddings

# Local application
from src.agents.base_agent import BaseAgent
from src.utils.config import load_config
```

### Error Handling

- Use custom exceptions from `src.utils.exceptions`
- Always log errors with appropriate context
- Provide meaningful error messages for debugging
- Clean up resources in `finally` blocks

### Configuration Management

- Use YAML for configuration files
- Environment variables for secrets (never commit `.env`)
- Provide sensible defaults in code
- Validate configurations at startup

---

## RAG Components

### Document Processing Pipeline

```python
from src.utils.document_processor import DocumentProcessor
from src.embeddings.model_loader import load_embedding_model
from src.vectorstore.chroma_store import ChromaStore

# Initialize components
processor = DocumentProcessor(chunk_size=512, overlap=50)
embedding_model = load_embedding_model("text-embedding-ada-002")
vector_store = ChromaStore(collection_name="documents")

# Process documents
documents = processor.load_and_chunk("data/documents/")
embeddings = embedding_model.embed_documents(documents)
vector_store.add_documents(documents, embeddings)
```

### Retrieval Strategies

1. **Dense Retrieval**: Vector similarity search
2. **Sparse Retrieval**: BM25 or TF-IDF
3. **Hybrid Retrieval**: Combination of dense and sparse
4. **Re-ranking**: Secondary scoring for retrieved documents

### Embedding Models

- **OpenAI**: `text-embedding-ada-002`, `text-embedding-3-small`
- **Open Source**: `sentence-transformers/all-MiniLM-L6-v2`
- **Domain-Specific**: Custom fine-tuned models

### Vector Stores

- **ChromaDB**: Lightweight, good for development
- **Pinecone**: Managed, production-ready
- **Qdrant**: Self-hosted, feature-rich
- **FAISS**: In-memory, high-performance

---

## Testing & Validation

### Test Categories

1. **Unit Tests**: Individual component functionality
2. **Integration Tests**: Component interactions
3. **End-to-End Tests**: Full pipeline validation
4. **Performance Tests**: Latency and throughput
5. **Quality Tests**: Output accuracy and relevance

### Evaluation Metrics

#### Retrieval Metrics
- **Recall@K**: Percentage of relevant documents in top-K results
- **Precision@K**: Percentage of top-K results that are relevant
- **MRR**: Mean Reciprocal Rank
- **NDCG**: Normalized Discounted Cumulative Gain

#### Generation Metrics
- **BLEU**: N-gram overlap with reference
- **ROUGE**: Recall-oriented overlap
- **BERTScore**: Semantic similarity
- **Human Evaluation**: Manual quality assessment

#### End-to-End Metrics
- **Answer Accuracy**: Correctness of final response
- **Latency**: Time to generate response
- **Token Usage**: Cost estimation
- **Context Relevance**: Quality of retrieved context

### Writing Tests

```python
import pytest
from src.agents.rag_agent import RAGAgent

@pytest.fixture
def rag_agent():
    """Create a RAG agent instance for testing."""
    config = load_test_config()
    agent = RAGAgent(config)
    yield agent
    agent.cleanup()

def test_query_processing(rag_agent):
    """Test basic query processing."""
    query = "What is RAG?"
    response = rag_agent.process_query(query)

    assert isinstance(response, str)
    assert len(response) > 0
    assert "retrieval" in response.lower()

def test_retrieval_accuracy(rag_agent):
    """Test retrieval quality."""
    query = "Explain vector embeddings"
    documents = rag_agent.retrieve_documents(query, k=5)

    assert len(documents) == 5
    assert all(doc.relevance_score > 0.5 for doc in documents)
```

---

## Common Tasks

### Task 1: Adding a New Document Source

```python
# 1. Create document loader in src/utils/document_loaders.py
class CustomDocumentLoader:
    def load(self, source: str) -> List[Document]:
        # Implementation
        pass

# 2. Register loader
from src.utils.document_processor import register_loader
register_loader("custom", CustomDocumentLoader)

# 3. Use in pipeline
processor = DocumentProcessor()
docs = processor.load_documents("source_path", loader_type="custom")
```

### Task 2: Implementing a Custom Agent

```python
from src.agents.base_agent import BaseAgent
from typing import List, Dict

class CustomRAGAgent(BaseAgent):
    """Custom RAG agent with specific behavior."""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.retriever = self._initialize_retriever()
        self.llm = self._initialize_llm()

    def process_query(self, query: str) -> str:
        """Process a query and return response."""
        # Retrieve relevant documents
        docs = self.retriever.retrieve(query, k=5)

        # Construct prompt with context
        context = "\n".join([doc.content for doc in docs])
        prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"

        # Generate response
        response = self.llm.generate(prompt)

        return response

    def _initialize_retriever(self):
        # Retriever setup
        pass

    def _initialize_llm(self):
        # LLM setup
        pass
```

### Task 3: Running Custom Evaluations

```python
from src.evaluation.evaluator import Evaluator
from src.evaluation.metrics import RetrievalMetrics, GenerationMetrics

# Load test dataset
test_queries = load_queries("data/queries/test_set.json")
ground_truth = load_ground_truth("data/ground_truth/test_answers.json")

# Initialize evaluator
evaluator = Evaluator(
    agent=my_agent,
    metrics=[RetrievalMetrics(), GenerationMetrics()]
)

# Run evaluation
results = evaluator.evaluate(
    queries=test_queries,
    ground_truth=ground_truth
)

# Generate report
evaluator.generate_report(results, output_path="reports/evaluation.html")
```

### Task 4: Debugging RAG Pipeline

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with trace mode
python -m src.harness --query "test query" --trace

# Inspect retrieved documents
python -m src.utils.inspect_retrieval --query "test query" --k 10

# Validate embeddings
python -m src.utils.validate_embeddings --sample 100
```

---

## Troubleshooting

### Common Issues

#### Issue: Low Retrieval Quality

**Symptoms**: Retrieved documents not relevant to query

**Solutions**:
- Check embedding model compatibility
- Verify document chunking parameters
- Tune similarity threshold
- Consider hybrid retrieval
- Implement re-ranking

```python
# Adjust retriever configuration
retriever_config = {
    "similarity_threshold": 0.7,  # Increase threshold
    "chunk_size": 256,            # Smaller chunks
    "enable_reranking": True      # Add re-ranking
}
```

#### Issue: Slow Query Response

**Symptoms**: High latency in query processing

**Solutions**:
- Optimize vector store indexing
- Reduce number of retrieved documents
- Enable caching for embeddings
- Use batch processing
- Profile code for bottlenecks

```python
# Enable caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_embedding(text: str):
    return embedding_model.encode(text)
```

#### Issue: Out of Memory Errors

**Symptoms**: Memory errors during document ingestion

**Solutions**:
- Process documents in batches
- Reduce embedding dimension
- Use streaming for large files
- Configure vector store memory limits

```python
# Batch processing example
def process_in_batches(documents, batch_size=100):
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        vector_store.add_documents(batch)
        gc.collect()  # Force garbage collection
```

#### Issue: API Rate Limits

**Symptoms**: Errors from embedding or LLM APIs

**Solutions**:
- Implement exponential backoff
- Use rate limiting middleware
- Cache responses
- Consider self-hosted alternatives

```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(5))
def call_api_with_retry(query):
    return api.embed(query)
```

### Getting Help

- Check existing issues and discussions
- Review documentation in `docs/`
- Run diagnostic scripts in `scripts/diagnostics/`
- Enable verbose logging for debugging
- Consult troubleshooting guide in wiki

---

## AI Assistant Guidelines

### When Working on This Codebase

1. **Always check configuration files** before modifying components
2. **Run tests after changes** to ensure nothing breaks
3. **Update documentation** when adding new features
4. **Follow the established patterns** in existing code
5. **Use type hints** for better code clarity
6. **Log important operations** for debugging
7. **Handle errors gracefully** with proper cleanup
8. **Optimize for readability** over cleverness

### Before Making Changes

- [ ] Understand the component's role in the pipeline
- [ ] Check existing tests for usage examples
- [ ] Review related configuration files
- [ ] Identify downstream dependencies
- [ ] Plan for backward compatibility

### After Making Changes

- [ ] Run full test suite
- [ ] Update relevant documentation
- [ ] Check for performance impact
- [ ] Validate with sample queries
- [ ] Update changelog if applicable

### Code Quality Standards

- **Test Coverage**: Aim for >80% coverage
- **Documentation**: All public APIs must be documented
- **Performance**: Benchmark critical paths
- **Security**: Validate all external inputs
- **Maintainability**: Keep functions focused and small

---

## Additional Resources

### Documentation

- **Architecture**: `docs/architecture.md`
- **API Reference**: `docs/api/`
- **Tutorials**: `docs/tutorials/`
- **FAQ**: `docs/faq.md`

### External Links

- [RAG Paper](https://arxiv.org/abs/2005.11401)
- [Vector Database Comparison](https://github.com/erikbern/ann-benchmarks)
- [LangChain RAG Guide](https://python.langchain.com/docs/use_cases/question_answering/)
- [Embedding Models Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)

### Community

- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share ideas
- Contributing: See CONTRIBUTING.md for guidelines

---

**Note for AI Assistants**: This document serves as the primary reference for understanding and working with the Agent-Harness-RAG codebase. When in doubt, refer to this guide and the existing code patterns. Prioritize code quality, test coverage, and clear documentation in all contributions.
