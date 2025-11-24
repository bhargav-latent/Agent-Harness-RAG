# PDF Preprocessing Scripts

This directory contains scripts for preprocessing PDF documents into markdown format for use with the RAG (Retrieval-Augmented Generation) system.

## Overview

The preprocessing pipeline converts PDF documents to markdown using the [marker](https://github.com/datalab-to/marker) API, making them ready for RAG integration with the Deep Agents harness.

## Directory Structure

```
Agent-Harness-RAG/
├── documents/              # Source PDF files
│   ├── attention_is_all_you_need.pdf
│   ├── The Essence of Software Engineering...pdf
│   └── thinkpython2.pdf
│
├── scripts/                # Preprocessing scripts
│   ├── preprocess_pdfs.py  # Main preprocessing script
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

## Workflow

### 1. Add PDFs

Place your PDF documents in the `documents/` directory:

```bash
cp /path/to/your/document.pdf documents/
```

### 2. Run Preprocessing

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

### 3. Use with RAG

The markdown files in `rag_data/processed/` are now ready for use with:
- Vector embedding
- Document chunking
- RAG retrieval
- Deep Agents integration

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

Potential improvements for the preprocessing pipeline:

- [ ] Incremental processing (skip already processed files)
- [ ] Parallel processing of multiple PDFs
- [ ] Custom chunking strategies for different document types
- [ ] Automatic embedding generation
- [ ] Vector database integration
- [ ] Document deduplication
- [ ] OCR support for scanned PDFs
- [ ] Progress bars for long-running jobs
- [ ] Retry logic with exponential backoff
- [ ] CLI with better argument parsing

## References

- **Marker Project:** https://github.com/datalab-to/marker
- **LangChain Deep Agents:** https://docs.langchain.com/oss/python/deepagents/
- **Project Documentation:** [../CLAUDE.md](../CLAUDE.md)
