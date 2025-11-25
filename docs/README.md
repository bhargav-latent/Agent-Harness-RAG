# Documentation

This folder contains all project documentation for Agent-Harness-RAG.

## Core Documentation

### [HYBRID_RAG_IMPLEMENTATION.md](HYBRID_RAG_IMPLEMENTATION.md) ⭐
**Complete guide to the Hybrid RAG implementation** - combines BM25 keyword matching with vector similarity search. Includes:
- Problem statement (vector search failure)
- Solution architecture (hybrid approach)
- Test results (5/5 perfect retrieval)
- Technical stack and deployment
- Journey from vector-only to hybrid

### [CLAUDE.md](CLAUDE.md)
**Deep Agents framework guide** - Comprehensive reference for AI assistants working with this codebase. Includes:
- What is Deep Agents
- Middleware system (TodoList, Filesystem, SubAgent)
- Backend storage (State, Filesystem, Store, Composite)
- RAG integration patterns
- Best practices and troubleshooting

## Deployment Guides

### [WSL_DEPLOYMENT.md](WSL_DEPLOYMENT.md) ⭐ **RECOMMENDED**
Complete WSL/Linux deployment guide:
- Why WSL (no Windows path bugs)
- Setup instructions
- Environment configuration
- Running agents

### [DEPLOYMENT.md](DEPLOYMENT.md)
General deployment instructions

### [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)
Deployment summary and quick reference

## Technical Guides

### [FILESYSTEM_BACKEND_FIX.md](FILESYSTEM_BACKEND_FIX.md)
FilesystemBackend configuration guide:
- Root cause analysis
- Configuration pattern (`virtual_mode=True`)
- Virtual path translation
- Best practices

### [WINDOWS_PATH_BUG.md](WINDOWS_PATH_BUG.md)
Windows path separator bug documentation:
- Bug description (malformed paths: `/\file.md`)
- GitHub Issue #340
- Agent-level workaround
- WSL alternative

### [VECTORSTORE_SETUP.md](VECTORSTORE_SETUP.md)
Vector store initialization and configuration

## Architecture Documents

### [AGENT_HARNESS.md](AGENT_HARNESS.md)
FileSearch RAG architecture details

### [VECTOR_STORE_RAG.md](VECTOR_STORE_RAG.md)
Vector Store RAG architecture details

## Quick Links

| Need | Document |
|------|----------|
| **Start here** | [../README.md](../README.md) |
| **Hybrid RAG guide** | [HYBRID_RAG_IMPLEMENTATION.md](HYBRID_RAG_IMPLEMENTATION.md) |
| **Deploy agents** | [WSL_DEPLOYMENT.md](WSL_DEPLOYMENT.md) |
| **Deep Agents framework** | [CLAUDE.md](CLAUDE.md) |
| **Fix Windows paths** | [WINDOWS_PATH_BUG.md](WINDOWS_PATH_BUG.md) |

## Documentation Organization

```
docs/
├── README.md                       # This file
├── HYBRID_RAG_IMPLEMENTATION.md    # ⭐ Hybrid RAG guide
├── CLAUDE.md                       # Deep Agents framework
├── WSL_DEPLOYMENT.md               # ⭐ Deployment (recommended)
├── DEPLOYMENT.md                   # General deployment
├── DEPLOYMENT_SUMMARY.md           # Deployment summary
├── FILESYSTEM_BACKEND_FIX.md       # Backend configuration
├── WINDOWS_PATH_BUG.md             # Windows bug workaround
├── VECTORSTORE_SETUP.md            # Vector store setup
├── AGENT_HARNESS.md                # FileSearch architecture
└── VECTOR_STORE_RAG.md             # Vector Store architecture
```

## Additional Resources

- **Main README**: [../README.md](../README.md)
- **Scripts Documentation**: [../scripts/README.md](../scripts/README.md)
- **Evaluation Framework**: [../evaluation/framework.md](../evaluation/framework.md)
- **Dataset Schema**: [../evaluation/dataset_schema.md](../evaluation/dataset_schema.md)
- **LangGraph Config**: [../langgraph.json](../langgraph.json)
