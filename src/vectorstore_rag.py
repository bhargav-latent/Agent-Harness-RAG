"""
Vector Store RAG - Standalone Class

This class provides a standalone interface to the Vector Store RAG agent
for programmatic use outside of LangGraph deployment.
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from deepagents import create_deep_agent
from deepagents.middleware import TodoListMiddleware
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools import tool

# Load environment variables
load_dotenv()

class VectorStoreRAG:
    """
    Vector Store RAG implementation using Deep Agents framework.

    Uses ChromaDB for vector similarity search to retrieve relevant document chunks
    based on semantic similarity.
    """

    def __init__(
        self,
        llm_base_url: str = None,
        llm_model: str = None,
        embeddings_base_url: str = None,
        embeddings_model: str = None,
        chroma_dir: str = None,
        temperature: float = 0.7,
        max_tokens: int = 8192
    ):
        """
        Initialize Vector Store RAG agent.

        Args:
            llm_base_url: LLM API endpoint
            llm_model: LLM model name
            embeddings_base_url: Embeddings API endpoint
            embeddings_model: Embeddings model name
            chroma_dir: ChromaDB persistence directory
            temperature: LLM temperature
            max_tokens: LLM max tokens
        """
        # Configuration
        self.llm_base_url = llm_base_url or os.getenv("LLM_BASE_URL")
        self.llm_model = llm_model or os.getenv("LLM_MODEL")
        self.embeddings_base_url = embeddings_base_url or os.getenv("EMBEDDINGS_BASE_URL")
        self.embeddings_model = embeddings_model or os.getenv("EMBEDDINGS_MODEL")
        self.chroma_dir = chroma_dir or os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

        # Initialize LLM
        self.llm = ChatOpenAI(
            base_url=self.llm_base_url,
            model=self.llm_model,
            api_key=os.getenv("OPENAI_API_KEY", "sk-placeholder"),
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            base_url=self.embeddings_base_url,
            model=self.embeddings_model,
            api_key=os.getenv("OPENAI_API_KEY", "sk-placeholder")
        )

        # Initialize vector store
        if not os.path.exists(self.chroma_dir):
            raise FileNotFoundError(
                f"ChromaDB vector store not found at {self.chroma_dir}. "
                "Please run 'python scripts/init_vectorstore.py' to initialize it."
            )

        self.vectorstore = Chroma(
            persist_directory=self.chroma_dir,
            embedding_function=self.embeddings,
            collection_name="rag_documents"
        )

        # Create tools
        @tool
        def vector_search(query: str, k: int = 5) -> str:
            """Search the vector store for documents relevant to the query."""
            try:
                results = self.vectorstore.similarity_search(query, k=k)
                if not results:
                    return "No relevant documents found."

                output = f"Retrieved {len(results)} relevant documents:\n\n"
                for i, doc in enumerate(results, 1):
                    source = doc.metadata.get('source', 'Unknown')
                    if '\\' in source or '/' in source:
                        source = source.split('\\')[-1].split('/')[-1]
                    output += f"--- Document {i} ({source}) ---\n"
                    output += doc.page_content
                    output += "\n\n"
                return output
            except Exception as e:
                return f"Error performing vector search: {str(e)}"

        @tool
        def vector_search_with_scores(query: str, k: int = 5) -> str:
            """Search the vector store and return documents with similarity scores."""
            try:
                results = self.vectorstore.similarity_search_with_relevance_scores(query, k=k)
                if not results:
                    return "No relevant documents found."

                output = f"Retrieved {len(results)} relevant documents with scores:\n\n"
                for i, (doc, score) in enumerate(results, 1):
                    source = doc.metadata.get('source', 'Unknown')
                    if '\\' in source or '/' in source:
                        source = source.split('\\')[-1].split('/')[-1]
                    output += f"--- Document {i} ({source}) - Relevance: {score:.3f} ---\n"
                    output += doc.page_content
                    output += "\n\n"
                return output
            except Exception as e:
                return f"Error performing vector search with scores: {str(e)}"

        # System prompt
        system_prompt = """You are a helpful assistant. Always use tools to answer user questions.

You have access to documents through semantic vector search:
- attention_is_all_you_need.md: Research paper about Transformer architecture
- thinkpython2.md: Python programming book
- The Essence of Software Engineering, Volker Gruhn, Rudiger Striemer.md: Software engineering book

Tools available:
- vector_search(query, k): Search for relevant documents using semantic similarity
- vector_search_with_scores(query, k): Same as vector_search but includes relevance scores

When answering questions:
1. Use vector_search to find relevant information from the documents
2. Base your answer on the retrieved content
3. Cite which document(s) you're referencing

Provide clear, accurate answers with citations."""

        # Create Deep Agent with planning middleware
        self.agent = create_deep_agent(
            model=self.llm,
            system_prompt=system_prompt,
            tools=[vector_search, vector_search_with_scores],
            middleware=[TodoListMiddleware()]
        )

    def query(self, question: str, chat_history: List = None) -> Dict[str, Any]:
        """
        Query the Vector Store RAG agent.

        Args:
            question: User question
            chat_history: Optional chat history (list of message dicts)

        Returns:
            Dict with:
                - question: Original question
                - answer: Agent's answer
                - messages: Full conversation messages
                - success: Boolean indicating success
                - error: Error message if failed
        """
        try:
            # Prepare messages
            messages = chat_history or []
            messages.append({"role": "user", "content": question})

            # Invoke agent
            result = self.agent.invoke({"messages": messages})

            # Extract answer
            final_message = result["messages"][-1]
            answer = final_message.content if hasattr(final_message, 'content') else str(final_message)

            return {
                "question": question,
                "answer": answer,
                "messages": result.get("messages", []),
                "success": True
            }

        except FileNotFoundError as e:
            return {
                "question": question,
                "answer": f"Vector store not initialized: {str(e)}",
                "error": str(e),
                "success": False
            }
        except Exception as e:
            return {
                "question": question,
                "answer": f"Error: {str(e)}",
                "error": str(e),
                "success": False
            }

    def search(self, query: str, k: int = 5, with_scores: bool = False) -> List[Dict[str, Any]]:
        """
        Direct vector similarity search (bypass agent).

        Args:
            query: Search query
            k: Number of results
            with_scores: Include relevance scores

        Returns:
            List of dicts with 'content', 'source', and optionally 'score'
        """
        try:
            if with_scores:
                results = self.vectorstore.similarity_search_with_relevance_scores(query, k=k)
                return [
                    {
                        "content": doc.page_content,
                        "source": doc.metadata.get('source', 'Unknown'),
                        "score": score
                    }
                    for doc, score in results
                ]
            else:
                results = self.vectorstore.similarity_search(query, k=k)
                return [
                    {
                        "content": doc.page_content,
                        "source": doc.metadata.get('source', 'Unknown')
                    }
                    for doc in results
                ]
        except Exception as e:
            raise RuntimeError(f"Vector search failed: {str(e)}")


# Example usage
if __name__ == "__main__":
    # Initialize RAG
    rag = VectorStoreRAG()

    # Example query
    question = "What is the attention mechanism in Transformers?"

    print(f"\nQuestion: {question}\n")
    print("="*80 + "\n")

    result = rag.query(question)

    if result["success"]:
        print(f"Answer:\n{result['answer']}\n")
    else:
        print(f"Error: {result['error']}\n")
