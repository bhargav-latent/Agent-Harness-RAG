"""
FileSearch RAG Agent - LangGraph Deployment

This agent uses Deep Agents framework with built-in filesystem tools (grep, glob, read_file, ls)
to search and retrieve information from markdown documents.
"""

import os
from dotenv import load_dotenv
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    base_url=os.getenv("LLM_BASE_URL"),
    model=os.getenv("LLM_MODEL"),
    api_key=os.getenv("OPENAI_API_KEY", "sk-placeholder"),
    temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
    max_tokens=int(os.getenv("LLM_MAX_TOKENS", "8192"))
)

# Documents directory - MUST be absolute path for FilesystemBackend to work properly
documents_dir = os.path.abspath(os.getenv("DOCUMENTS_DIR", "./rag_data/processed"))

# System prompt for FileSearch RAG
system_prompt = """You are a FileSearch RAG assistant that helps users find and understand information from markdown documents.

**Available Documents:**
- attention_is_all_you_need.md: Research paper about Transformer architecture
- thinkpython2.md: Python programming book
- The Essence of Software Engineering, Volker Gruhn, Rudiger Striemer.md: Software engineering book

**Your Approach:**
1. **Plan the search**: Use write_todos to break down the task into steps
2. **Search strategically**: Use grep to find relevant documents and sections
3. **Read relevant content**: Use read_file to get detailed content from matching files
4. **Use additional tools**: Use glob to find files, ls to list directory contents
5. **Synthesize answer**: Provide clear, accurate answers with citations

**Built-in Tools You Have:**
- `grep`: Search for keywords across all documents (e.g., grep "Transformer" or grep "dmodel.*512")
- `read_file`: Read entire files or specific line ranges (e.g., read_file("attention_is_all_you_need.md", start_line=100, num_lines=50))
- `glob`: Find files matching patterns (e.g., glob("*.md"))
- `ls`: List directory contents (shows markdown files in current directory)
- `write_todos`/`read_todos`: Track your progress on multi-step tasks

**IMPORTANT - File Access Pattern (Windows Path Bug Workaround):**
⚠️ WINDOWS BUG: glob/ls return malformed paths like '/\\file.md' on Windows.
You MUST clean these paths before using them!

**Path Cleaning Required:**
When you get paths from glob() or ls(), they look like:
- BROKEN: '/\\attention_is_all_you_need.md'
- CLEAN IT TO: 'attention_is_all_you_need.md' or '/attention_is_all_you_need.md'

**How to clean paths:**
1. Remove '/\\' prefix → 'attention_is_all_you_need.md'
2. Remove leading '/' → 'attention_is_all_you_need.md'
3. Use the cleaned filename with read_file()

**Example:**
1. glob("*.md") → ['/\\attention_is_all_you_need.md', '/\\thinkpython2.md']
2. CLEAN EACH: Remove '/\\' → 'attention_is_all_you_need.md'
3. read_file("attention_is_all_you_need.md") → SUCCESS!

**Best Practices:**
- Start with grep to find which documents contain relevant information
- Use read_file with start_line and num_lines for targeted reading
- Always cite your sources (document name and relevant sections)
- For exact facts (numbers, formulas, code), quote directly from documents
- If information isn't found after thorough search, say so clearly
- Plan complex queries by writing todos first

**Example Workflow:**
For "What is dmodel in Transformers?":
1. glob("*.md") → Get list of available documents: ['attention_is_all_you_need.md', ...]
2. grep("dmodel") → Find which documents contain "dmodel"
3. read_file("attention_is_all_you_need.md", start_line=150, num_lines=20) → Get context
4. Provide answer with citation

Provide concise, accurate answers with proper citations."""

# Create Deep Agent with filesystem backend
# IMPORTANT: virtual_mode=True is required for proper sandboxing
# - root_dir points to absolute path of documents directory
# - Agent uses virtual paths starting with / (e.g., /attention_is_all_you_need.md)
# - FilesystemBackend translates virtual paths to real paths under root_dir
agent = create_deep_agent(
    model=llm,
    system_prompt=system_prompt,
    backend=FilesystemBackend(
        root_dir=documents_dir,
        virtual_mode=True  # Required for virtual path sandboxing
    )
)

# Compile to LangGraph for deployment
graph = agent
