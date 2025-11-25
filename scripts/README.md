# Scripts

This directory contains essential scripts for document preprocessing and RAG system setup.

## Overview

Two core scripts prepare documents for the RAG (Retrieval-Augmented Generation) system:

1. **preprocess_pdfs.py** - Converts PDFs to markdown using marker API
2. **init_vectorstore.py** - Initializes ChromaDB vector store with embeddings

Diagnostic and test scripts have been archived in `archive/` for reference.

## Directory Structure

```
Agent-Harness-RAG/
├── documents/              # Source PDF files
│   ├── attention_is_all_you_need.pdf
│   ├── The Essence of Software Engineering...pdf
│   └── thinkpython2.pdf
│
├── scripts/                # Setup scripts
│   ├── preprocess_pdfs.py  # PDF to markdown conversion
│   ├── init_vectorstore.py # Vector store initialization
│   ├── archive/            # Archived test/diagnostic scripts
│   └── README.md           # This file
│
├── rag_data/               # Processed data for RAG
│   ├── processed/          # Converted markdown files
│   │   ├── attention_is_all_you_need.md
│   │   ├── The Essence of Software Engineering...md
│   │   └── thinkpython2.md
│   └── metadata.json       # Processing metadata and statistics
│
└── CLAUDE.md               # Project documentation
```

## Scripts

### preprocess_pdfs.py

Main preprocessing script that:
- Scans the `documents/` directory for PDF files
- Converts each PDF to markdown via the marker API
- Saves markdown files to `rag_data/processed/`
- Maintains metadata about processing in `rag_data/metadata.json`

**Basic Usage:**

```bash
# Process all PDFs in default directories
python scripts/preprocess_pdfs.py

# Specify custom directories
python scripts/preprocess_pdfs.py \
  --input-dir path/to/pdfs \
  --output-dir path/to/output

# Use different API endpoint
python scripts/preprocess_pdfs.py \
  --api-url http://custom-host:port/analyze
```

**Arguments:**

- `--input-dir`: Directory containing PDF files (default: `documents`)
- `--output-dir`: Directory to save markdown files (default: `rag_data/processed`)
- `--api-url`: API endpoint URL (default: `http://10.26.1.11:8701/analyze`)

**Requirements:**

```bash
pip install requests
```

**Features:**

- ✅ Batch processing of multiple PDFs
- ✅ API health checking before processing
- ✅ Progress tracking with visual feedback
- ✅ Error handling and reporting
- ✅ Metadata tracking (timestamps, file sizes, success status)
- ✅ UTF-8 encoding support for Windows
- ✅ Automatic directory creation
- ✅ Timeout handling for large files (5 minute default)

---

### init_vectorstore.py

Initializes ChromaDB vector store with embeddings from preprocessed markdown documents.

**Basic Usage:**

```bash
# Initialize vector store with default settings
python scripts/init_vectorstore.py
```

**What it does:**

1. Loads markdown documents from `rag_data/processed/`
2. Chunks documents using RecursiveCharacterTextSplitter (512 chars, 50 overlap)
3. Generates embeddings using Qwen/Qwen3-Embedding-8B (4096 dimensions)
4. Stores embeddings in ChromaDB at `chroma_db/`
5. Creates persistent collection named "rag_documents"

**Requirements:**

```bash
pip install langchain langchain-openai langchain-chroma langchain-community python-dotenv
```

**Configuration (.env):**

```bash
EMBEDDINGS_BASE_URL=http://10.26.1.11:8786/v1
EMBEDDINGS_MODEL=Qwen/Qwen3-Embedding-8B
DOCUMENTS_DIR=./rag_data/processed
CHROMA_PERSIST_DIR=./chroma_db
CHUNK_SIZE=512
CHUNK_OVERLAP=50
```

**Example Output:**

```
Initializing ChromaDB vector store...

Configuration:
  Documents dir: ./rag_data/processed
  ChromaDB dir: ./chroma_db
  Embeddings model: Qwen/Qwen3-Embedding-8B
  Chunk size: 512
  Chunk overlap: 50

Loading documents...
[OK] Loaded 3 documents

Chunking documents...
[OK] Created 3,370 chunks

Generating embeddings and storing in ChromaDB...
[OK] Vector store initialized with 3,370 embeddings

ChromaDB collection: rag_documents
```

**Features:**

- ✅ Automatic chunking with configurable size/overlap
- ✅ Persistent vector store (survives restarts)
- ✅ Progress tracking
- ✅ Proper encoding handling (UTF-8)
- ✅ Collection name validation

---

## Archive Folder

The `archive/` directory contains diagnostic and test scripts used during development. These scripts helped identify and solve:

- Vector search low relevance score issue (0.19-0.27)
- BM25 vs vector search comparison (5/5 vs 1/5 results)
- Hybrid retrieval validation (5/5 perfect results)
- ChromaDB configuration debugging

**See:** [archive/README.md](archive/README.md) for complete documentation of archived scripts.

---

## API Endpoint

The preprocessing script uses the marker API for PDF to markdown conversion:

**Endpoint:** `POST /analyze`

**Request:**
- Content-Type: `multipart/form-data`
- Body: `files` (one or more PDF files)

**Response:**
```json
{
  "results": [
    {
      "file_name": "document.pdf",
      "file_type": "pdf",
      "success": true,
      "processing_method": "Marker PdfConverter",
      "analysis_type": "Full PDF conversion to markdown",
      "content": "# Markdown content here..."
    }
  ]
}
```

**Health Check:** `GET /health`

## Metadata File

The `rag_data/metadata.json` file tracks all processed documents:

```json
{
  "processed_files": [
    {
      "pdf_file": "documents\\attention_is_all_you_need.pdf",
      "pdf_name": "attention_is_all_you_need.pdf",
      "markdown_file": "rag_data\\processed\\attention_is_all_you_need.md",
      "success": true,
      "processed_at": "2025-11-24T15:36:41.379094",
      "file_size_bytes": 2215244
    }
  ],
  "last_updated": "2025-11-24T15:40:06.466159",
  "total_processed": 3,
  "successful": 3
}
```

This metadata is useful for:
- Tracking which documents have been processed
- Monitoring processing success rates
- Debugging failed conversions
- Avoiding reprocessing of unchanged files

## Complete Workflow

### 1. Add PDFs

Place your PDF documents in the `documents/` directory:

```bash
cp /path/to/your/document.pdf documents/
```

### 2. Convert PDFs to Markdown

Execute the preprocessing script:

```bash
python scripts/preprocess_pdfs.py
```

**Example Output:**

```
============================================================
PDF to Markdown Preprocessing Pipeline
============================================================
Input directory:  documents
Output directory: rag_data\processed
API endpoint:     http://10.26.1.11:8701/analyze
============================================================
✅ API is healthy
📄 Found 3 PDF file(s) in documents

🔄 Processing: attention_is_all_you_need.pdf
✅ Successfully converted: attention_is_all_you_need.pdf
💾 Saved markdown: rag_data\processed\attention_is_all_you_need.md

============================================================
Processing Complete!
============================================================
Total PDFs:       3
✅ Successful:    3
❌ Failed:        0
```

### 3. Initialize Vector Store

Generate embeddings and store in ChromaDB:

```bash
python scripts/init_vectorstore.py
```

**Example Output:**

```
Initializing ChromaDB vector store...
[OK] Loaded 3 documents
[OK] Created 3,370 chunks
[OK] Vector store initialized with 3,370 embeddings
```

### 4. Deploy RAG Agents

The processed documents are now ready for all 4 RAG agents:

```bash
langgraph dev
```

Access agents at http://localhost:2024:
- **filesearch_agent** - grep/glob/read_file search
- **vectorstore_agent** - Vector similarity search
- **bm25_agent** - BM25 keyword search
- **hybrid_rag_agent** - ⭐ **RECOMMENDED** - Hybrid BM25 + vector

**See:** [../HYBRID_RAG_IMPLEMENTATION.md](../HYBRID_RAG_IMPLEMENTATION.md) for agent details

## Integration with Deep Agents

The processed markdown files can be used with Deep Agents RAG middleware:

```python
from deepagents import create_deep_agent
from deepagents.middleware import FilesystemMiddleware
from deepagents.backends import FilesystemBackend

# Create agent with access to processed documents
agent = create_deep_agent(
    model="gpt-4",
    backend=FilesystemBackend(
        root_dir="./rag_data/processed",
        virtual=True
    ),
    middleware=[FilesystemMiddleware()],
    system_prompt="You have access to processed documents. Use read_file to access them."
)

# Agent can now read processed markdown files
response = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "What does the Attention is All You Need paper discuss?"
    }]
})
```

## Troubleshooting

### API Connection Issues

**Problem:** `❌ API health check failed: Connection refused`

**Solutions:**
- Verify the API server is running: `curl http://10.26.1.11:8701/health`
- Check network connectivity to the API host
- Verify firewall settings allow connections
- Try using `--api-url` with a different endpoint

### Unicode Encoding Errors (Windows)

**Problem:** `UnicodeEncodeError: 'charmap' codec can't encode character`

**Solution:** The script automatically handles this. If issues persist, ensure you're using Python 3.6+.

### Large File Timeouts

**Problem:** Processing times out for large PDFs

**Solution:** The script has a 5-minute timeout per file. For larger files, you may need to:
- Increase the timeout in the script (line 90: `timeout=300`)
- Split large PDFs into smaller chunks
- Use a more powerful API backend

### Failed Conversions

**Problem:** Some PDFs fail to convert

**Check:**
- PDF file is not corrupted: Try opening it manually
- PDF file is not password-protected
- Check `metadata.json` for error details
- Review API logs on the server side

## Future Enhancements

Potential improvements:

**Preprocessing:**
- [ ] Incremental processing (skip already processed files based on metadata)
- [ ] Parallel processing of multiple PDFs
- [ ] OCR support for scanned PDFs
- [ ] Progress bars for long-running jobs
- [ ] Retry logic with exponential backoff

**Vector Store:**
- [ ] Re-ranking with cross-encoder (BAAI/bge-reranker-base)
- [ ] Reciprocal Rank Fusion (RRF) for hybrid search
- [ ] Document-aware retrieval (filter by document intent)
- [ ] Custom chunking strategies per document type
- [ ] Incremental updates (add new documents without rebuild)

**Evaluation:**
- [ ] Automated evaluation with 50 test questions
- [ ] RAGAS metrics (answer_relevancy, faithfulness, context_precision)
- [ ] Performance comparison across 4 agents
- [ ] Category-specific analysis (12 question types)

## References

### Documentation
- **Project Overview:** [../README.md](../README.md)
- **Deep Agents Guide:** [../CLAUDE.md](../CLAUDE.md)
- **Hybrid RAG Implementation:** [../HYBRID_RAG_IMPLEMENTATION.md](../HYBRID_RAG_IMPLEMENTATION.md)

### Technologies
- **Marker PDF Converter:** https://github.com/datalab-to/marker
- **LangChain Deep Agents:** https://docs.langchain.com/oss/python/deepagents/
- **ChromaDB:** https://docs.trychroma.com/
- **LangGraph Deployment:** https://langchain-ai.github.io/langgraph/
