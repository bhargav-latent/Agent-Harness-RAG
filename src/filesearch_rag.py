"""
FileSearch RAG Agent using Deep Agents Framework

This agent uses the built-in filesystem tools (grep, glob, read_file, ls) from Deep Agents
to search and retrieve information from markdown documents, then generates answers using an LLM.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()


class FileSearchRAG:
    """FileSearch RAG Agent using Deep Agents Framework"""

    def __init__(
        self,
        llm_base_url: str = None,
        llm_model: str = None,
        documents_dir: str = None,
        temperature: float = 0.7,
        max_tokens: int = 8192
    ):
        self.documents_dir = documents_dir or os.getenv("DOCUMENTS_DIR", "./rag_data/processed")

        # Verify documents directory exists
        documents_path = Path(self.documents_dir)
        if not documents_path.exists():
            raise ValueError(f"Documents directory not found: {self.documents_dir}")

        # Initialize LLM
        self.llm = ChatOpenAI(
            base_url=llm_base_url or os.getenv("LLM_BASE_URL"),
            model=llm_model or os.getenv("LLM_MODEL"),
            api_key=os.getenv("OPENAI_API_KEY", "sk-placeholder"),
            temperature=temperature,
            max_tokens=max_tokens
        )

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
- `ls`: List directory contents
- `write_todos`/`read_todos`: Track your progress on multi-step tasks

**Best Practices:**
- Start with grep to find which documents contain relevant information
- Use read_file with start_line and num_lines for targeted reading
- Always cite your sources (document name and relevant sections)
- For exact facts (numbers, formulas, code), quote directly from documents
- If information isn't found after thorough search, say so clearly
- Plan complex queries by writing todos first

**Example Workflow:**
For "What is dmodel in Transformers?":
1. write_todos: ["Search for 'dmodel' in documents", "Read relevant sections", "Synthesize answer"]
2. grep "dmodel" → Find: attention_is_all_you_need.md:line 156
3. read_file("attention_is_all_you_need.md", start_line=150, num_lines=20) → Get context
4. Provide answer with citation

Provide concise, accurate answers with proper citations."""

        # Create Deep Agent with filesystem backend pointing to documents directory
        # IMPORTANT: virtual_mode=True is required for proper sandboxing
        # - root_dir points to absolute path of documents directory
        # - Agent uses virtual paths starting with / (e.g., /attention_is_all_you_need.md)
        # - FilesystemBackend translates virtual paths to real paths under root_dir
        self.agent = create_deep_agent(
            model=self.llm,
            system_prompt=system_prompt,
            backend=FilesystemBackend(
                root_dir=os.path.abspath(self.documents_dir),
                virtual_mode=True  # Required for virtual path sandboxing
            )
        )

    def query(self, question: str, chat_history: List = None) -> Dict[str, Any]:
        """
        Query the FileSearch RAG system

        Args:
            question: The user's question
            chat_history: Optional conversation history (list of messages)

        Returns:
            Dictionary with answer, messages, and metadata
        """
        try:
            # Build messages list
            messages = chat_history or []
            messages.append({"role": "user", "content": question})

            # Invoke Deep Agent
            result = self.agent.invoke({"messages": messages})

            # Extract the final answer from the last message
            final_message = result["messages"][-1]
            answer = final_message.content if hasattr(final_message, 'content') else str(final_message)

            return {
                "question": question,
                "answer": answer,
                "messages": result.get("messages", []),
                "success": True
            }
        except Exception as e:
            return {
                "question": question,
                "answer": f"Error processing question: {str(e)}",
                "error": str(e),
                "success": False
            }


# Example usage
if __name__ == "__main__":
    # Initialize FileSearch RAG
    rag = FileSearchRAG()

    # Test query
    test_question = "What is the value of dmodel used in the Transformer architecture?"
    print(f"\nQuestion: {test_question}\n")

    result = rag.query(test_question)

    print(f"\nAnswer: {result['answer']}\n")
    print(f"Success: {result['success']}\n")
