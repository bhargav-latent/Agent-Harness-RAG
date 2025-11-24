# Deep Agents FilesystemBackend Configuration - Root Cause Analysis

## Problem

The FileSearch RAG agent was unable to access files in the documents directory. Tools like `glob`, `ls`, `grep`, and `read_file` were failing with:
- "File not found" errors
- "No matches found" for grep
- Empty directory listings

## Root Cause

**Incorrect Understanding of Deep Agents FilesystemBackend Configuration**

The issue was caused by misunderstanding how Deep Agents FilesystemBackend works with `virtual_mode` parameter:

### INCORRECT Configuration ❌
```python
agent = create_deep_agent(
    model=llm,
    system_prompt=system_prompt,
    backend=FilesystemBackend(
        root_dir=documents_dir,  # Relative path
        virtual_mode=False        # WRONG!
    )
)
```

**Problems:**
1. `virtual_mode=False` attempts to use absolute Windows paths
2. FilesystemBackend **REJECTS** Windows absolute paths with error:
   ```
   ValueError: Windows absolute paths are not supported: D:\Personal Projects\...
   Please use virtual paths starting with / (e.g., /workspace/file.txt)
   ```

### CORRECT Configuration ✅
```python
agent = create_deep_agent(
    model=llm,
    system_prompt=system_prompt,
    backend=FilesystemBackend(
        root_dir=os.path.abspath(documents_dir),  # Absolute path
        virtual_mode=True                          # CORRECT!
    )
)
```

**How it works:**
1. `root_dir` must be an **absolute path** (e.g., `D:\...\rag_data\processed`)
2. `virtual_mode=True` enables virtual path sandboxing
3. Agent uses **virtual paths** starting with `/` (e.g., `/attention_is_all_you_need.md`)
4. FilesystemBackend translates virtual paths to real paths under `root_dir`

## The Pattern

### Backend Configuration
```python
documents_dir = os.path.abspath("./rag_data/processed")

backend=FilesystemBackend(
    root_dir=documents_dir,    # Must be absolute path
    virtual_mode=True           # Required for virtual path sandboxing
)
```

### Agent Usage
Agent tools work with virtual paths:
```python
# Correct usage in agent
glob("*.md")                                    # Returns ['attention_is_all_you_need.md', ...]
ls("/")                                         # Lists all files in virtual root
grep("attention")                               # Searches all files
read_file("attention_is_all_you_need.md")      # Reads the file
```

### System Prompt Instructions
Tell the agent to use virtual paths:
```
Your filesystem backend uses virtual paths starting with / (not Windows paths).
- glob("*.md") → returns ['attention_is_all_you_need.md', 'thinkpython2.md', ...]
- read_file("attention_is_all_you_need.md") → reads the file
- grep searches all files in the virtual root
- ls("/") → lists all files in the documents directory
- Use simple filenames like "attention_is_all_you_need.md", NOT absolute paths
```

## Security

This configuration provides proper sandboxing:
- Agent can ONLY access files under `root_dir` (documents directory)
- Agent CANNOT access files outside the sandboxed directory
- All paths are relative to the virtual root (`root_dir`)

## Files Updated

1. **agents/filesearch_agent.py** - LangGraph deployment agent
   - Changed `virtual_mode=False` → `virtual_mode=True`
   - Updated system prompt to explain virtual path usage
   - Added absolute path conversion for `root_dir`

2. **src/filesearch_rag.py** - Standalone FileSearch RAG class
   - Changed `virtual_mode=False` → `virtual_mode=True`
   - Added absolute path conversion for `root_dir`

3. **test_agent_access.py** - Test script
   - Created to verify filesystem tools work correctly
   - Tests glob, ls, grep, and read_file tools

## Verification

Test results confirm the fix works:
```
glob("*.md") → ['/\\attention_is_all_you_need.md', '/\\thinkpython2.md', ...]
ls("/") → [same list]
grep("attention") → Found files containing "attention"
```

All filesystem tools now function correctly with virtual path sandboxing.

## Key Takeaways

1. **Deep Agents FilesystemBackend requires `virtual_mode=True` for proper operation**
2. **`root_dir` must be an absolute path**
3. **Agent uses virtual paths (starting with `/`), NOT Windows paths**
4. **FilesystemBackend translates virtual→real paths automatically**
5. **This pattern provides secure filesystem sandboxing**

## References

- Deep Agents Documentation: https://docs.langchain.com/oss/python/deepagents/backends
- Error message that revealed the issue:
  ```
  ValueError: Windows absolute paths are not supported: D:\Personal Projects\...
  Please use virtual paths starting with / (e.g., /workspace/file.txt)
  ```
