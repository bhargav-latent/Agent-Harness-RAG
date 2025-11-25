# Deploying FileSearch RAG Agent with WSL

## Why WSL?

WSL (Windows Subsystem for Linux) provides a native Linux environment on Windows, which **completely avoids the Deep Agents Windows path bug**. The FilesystemBackend works perfectly on Linux without any path separator issues.

## Prerequisites

1. **WSL2 Installed** - Check with `wsl --status` in PowerShell
2. **Ubuntu or another Linux distro** - Check with `wsl -l -v`
3. **Python 3.10+** installed in WSL

## Setup Guide

### Step 1: Access Your Project in WSL

Windows drives are mounted in WSL under `/mnt/`:

```bash
# Open WSL terminal
wsl

# Navigate to your project
cd "/mnt/d/Personal Projects/Agent-Harness-RAG"

# Verify you're in the right place
pwd
ls
```

**Expected output:**
```
/mnt/d/Personal Projects/Agent-Harness-RAG
agents/  documents/  rag_data/  src/  ...
```

### Step 2: Set Up Python Virtual Environment (WSL)

```bash
# Install Python and pip if not already installed
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Create virtual environment
python3 -m venv venv_wsl

# Activate it
source venv_wsl/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Verify Deep Agents is installed
pip show deepagents
```

### Step 4: Configure Environment Variables

The `.env` file should work as-is, but verify the LLM endpoint is accessible from WSL:

```bash
# Test LLM connectivity
curl http://10.26.1.56:8708/v1/models

# If that works, you're good to go!
```

**If you need to modify `.env` for WSL:**
```bash
# Copy and edit if needed
cp .env .env.wsl
nano .env.wsl
```

### Step 5: Verify File Access

Test that Python can access the documents:

```bash
# Quick test
python3 -c "
import os
docs_dir = os.path.abspath('./rag_data/processed')
print(f'Documents: {docs_dir}')
print(f'Files: {os.listdir(docs_dir)}')
"
```

**Expected output:**
```
Documents: /mnt/d/Personal Projects/Agent-Harness-RAG/rag_data/processed
Files: ['attention_is_all_you_need.md', 'thinkpython2.md', ...]
```

### Step 6: Run LangGraph Dev Server in WSL

```bash
# Make sure you're in the project root
cd "/mnt/d/Personal Projects/Agent-Harness-RAG"

# Activate virtual environment
source venv_wsl/bin/activate

# Start LangGraph dev server
langgraph dev
```

**Expected output:**
```
Welcome to

█   ██ ██ ██ ╔═╗┬─┐┌─┐┌─┐┬ ┬
█   ├─┤││││ ├─┬║ ╬├┬┘├─┤├─┘├─┤
╚═╝ ┴ ┴└┘└┘└─┘╚═╝┴└─┴ ┴┴  ┴ ┴

- 🚀 API: http://127.0.0.1:2024
- 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- 📚 API Docs: http://127.0.0.1:2024/docs
```

### Step 7: Access from Windows Browser

The server runs on `127.0.0.1:2024` which is accessible from both WSL and Windows:

**Open in Windows browser:**
- Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- API Docs: http://127.0.0.1:2024/docs
- Direct API: http://127.0.0.1:2024

## Verification Test

### Test 1: Check Paths Work Correctly

In WSL, run the test script:

```bash
source venv_wsl/bin/activate
python test_tool_outputs.py
```

**Expected (WSL - Fixed):**
```
glob("*.md") → ['/attention_is_all_you_need.md', '/thinkpython2.md']
```

**Compare to Windows (Broken):**
```
glob("*.md") → ['/\\attention_is_all_you_need.md', '/\\thinkpython2.md']
                  ^^^ Mixed separators - BROKEN on Windows
```

### Test 2: Query the Agent

```bash
# Test query via Python
python3 -c "
from src.filesearch_rag import FileSearchRAG

rag = FileSearchRAG()
result = rag.query('What is the attention mechanism?')
print(result['answer'])
"
```

Should return a proper answer from the `attention_is_all_you_need.md` document!

## Development Workflow

### Editing Files

**Option 1: Edit in Windows, Run in WSL**
- Edit files using Windows VSCode/editor
- Files at `D:\Personal Projects\Agent-Harness-RAG\`
- Run/test in WSL terminal
- Changes are immediately visible in WSL

**Option 2: VSCode Remote - WSL**
```bash
# In WSL terminal
cd "/mnt/d/Personal Projects/Agent-Harness-RAG"
code .
```
This opens VSCode in "WSL mode" where everything runs natively in Linux.

### File Watching / Auto-Reload

LangGraph dev server auto-reloads when files change, whether you edit in Windows or WSL:

```bash
# Server is running in WSL
langgraph dev

# Edit agents/filesearch_agent.py in Windows
# Server automatically detects change and reloads ✓
```

## Performance Considerations

### File I/O Performance

WSL2 accessing Windows files (`/mnt/d/...`) has some overhead. For better performance:

**Option 1: Keep files in Windows (Current Setup)**
- ✅ Easy to edit with Windows tools
- ✅ Shared with Windows apps
- ⚠️ Slightly slower I/O
- **Good for development**

**Option 2: Copy to WSL Native Filesystem**
```bash
# Copy project to WSL home
cp -r "/mnt/d/Personal Projects/Agent-Harness-RAG" ~/agent-rag
cd ~/agent-rag
langgraph dev
```
- ✅ Faster I/O
- ✅ True Linux performance
- ⚠️ Need to sync changes
- **Good for production/benchmarking**

## Environment Variables

### Using Windows .env in WSL

The `.env` file works directly:

```bash
# WSL automatically reads .env from project root
cd "/mnt/d/Personal Projects/Agent-Harness-RAG"
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print(os.getenv('LLM_BASE_URL'))
"
# Output: http://10.26.1.56:8708/v1
```

### Network Configuration

Your LLM server at `10.26.1.56:8708` should be accessible from WSL. Test:

```bash
# Check connectivity
curl http://10.26.1.56:8708/v1/models

# Or
ping 10.26.1.56
```

If network issues occur, you may need to configure WSL networking (usually not needed).

## Troubleshooting

### Issue: "Cannot find module deepagents"

```bash
# Make sure virtual environment is activated
source venv_wsl/bin/activate

# Verify installation
pip list | grep deepagents

# Reinstall if needed
pip install deepagents
```

### Issue: "Permission denied" on /mnt/d/

```bash
# Check file permissions
ls -la "/mnt/d/Personal Projects/Agent-Harness-RAG"

# If needed, fix permissions (use with caution)
chmod -R u+rw "/mnt/d/Personal Projects/Agent-Harness-RAG"
```

### Issue: LangGraph server won't start

```bash
# Check if port 2024 is already in use
netstat -tuln | grep 2024

# Kill existing process if needed
pkill -f langgraph

# Or use a different port
langgraph dev --port 2025
```

### Issue: Can't access server from Windows browser

```bash
# Make sure server is listening on 0.0.0.0 or 127.0.0.1
# Check with:
netstat -tuln | grep 2024

# Expected: 0.0.0.0:2024 or 127.0.0.1:2024
```

## Production Deployment

### Running as Background Service

```bash
# Install tmux or screen
sudo apt install tmux

# Start tmux session
tmux new -s agent-rag

# Run server
cd "/mnt/d/Personal Projects/Agent-Harness-RAG"
source venv_wsl/bin/activate
langgraph dev

# Detach: Ctrl+B, then D
# Reattach: tmux attach -t agent-rag
```

### Systemd Service (Advanced)

Create `/etc/systemd/system/agent-rag.service`:

```ini
[Unit]
Description=FileSearch RAG Agent
After=network.target

[Service]
Type=simple
User=YOUR_WSL_USERNAME
WorkingDirectory=/mnt/d/Personal Projects/Agent-Harness-RAG
Environment="PATH=/mnt/d/Personal Projects/Agent-Harness-RAG/venv_wsl/bin"
ExecStart=/mnt/d/Personal Projects/Agent-Harness-RAG/venv_wsl/bin/langgraph dev
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable agent-rag
sudo systemctl start agent-rag
sudo systemctl status agent-rag
```

## Comparison: Windows vs WSL

| Aspect | Windows Native | WSL |
|--------|---------------|-----|
| **Path Bug** | ❌ Malformed `/\` paths | ✅ Clean `/` paths |
| **FilesystemBackend** | ⚠️ Requires workaround | ✅ Works natively |
| **File Editing** | ✅ Native Windows tools | ✅ Same files via /mnt |
| **Performance** | ✅ Native I/O | ⚠️ Slight overhead on /mnt |
| **Setup Complexity** | ✅ Simple | ⚠️ Requires WSL |
| **Compatibility** | ⚠️ Deep Agents bug | ✅ Full compatibility |
| **Recommended For** | ❓ Wait for bug fix | ✅ **Use this now!** |

## Summary

**Quick Start:**
```bash
# 1. Open WSL
wsl

# 2. Navigate to project
cd "/mnt/d/Personal Projects/Agent-Harness-RAG"

# 3. Create & activate venv
python3 -m venv venv_wsl
source venv_wsl/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run server
langgraph dev

# 6. Open in Windows browser
# http://127.0.0.1:2024
```

**Benefits:**
- ✅ **Zero path bugs** - Linux handles paths correctly
- ✅ **Full Deep Agents compatibility** - Works as designed
- ✅ **Same files** - Edit in Windows, run in WSL
- ✅ **Production ready** - Can deploy to real Linux servers later

This is the **recommended approach** until the Deep Agents Windows path bug (PR #336) is merged!
