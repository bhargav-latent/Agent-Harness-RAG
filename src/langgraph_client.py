"""
LangGraph API Client for Benchmark Evaluation

This module provides a client to invoke LangGraph agents via HTTP API.
"""

import json
import time
import uuid
import requests
from typing import Optional
from dataclasses import dataclass


@dataclass
class AgentResponse:
    """Response from a LangGraph agent invocation."""
    answer: str
    tool_calls: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: float
    success: bool
    error: Optional[str] = None
    raw_messages: list = None


class LangGraphClient:
    """Client for invoking LangGraph agents via HTTP API."""

    def __init__(self, base_url: str = "http://127.0.0.1:2026"):
        """
        Initialize the LangGraph client.

        Args:
            base_url: Base URL of the LangGraph server
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def invoke(self, graph_name: str, question: str, timeout: int = 300) -> AgentResponse:
        """
        Invoke a LangGraph agent with a question.

        Args:
            graph_name: Name of the graph (e.g., "hybrid_rag_agent", "filesearch_agent")
            question: The question to ask
            timeout: Request timeout in seconds

        Returns:
            AgentResponse with answer, metrics, and metadata
        """
        thread_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            # Create a thread first
            thread_response = self.session.post(
                f"{self.base_url}/threads",
                json={"thread_id": thread_id},
                timeout=30
            )

            # Invoke the graph with streaming disabled for simpler parsing
            run_response = self.session.post(
                f"{self.base_url}/threads/{thread_id}/runs/wait",
                json={
                    "assistant_id": graph_name,
                    "input": {
                        "messages": [
                            {"role": "user", "content": question}
                        ]
                    },
                    "config": {
                        "configurable": {}
                    }
                },
                timeout=timeout
            )

            latency_ms = (time.time() - start_time) * 1000

            if run_response.status_code != 200:
                return AgentResponse(
                    answer="",
                    tool_calls=0,
                    input_tokens=0,
                    output_tokens=0,
                    total_tokens=0,
                    latency_ms=latency_ms,
                    success=False,
                    error=f"HTTP {run_response.status_code}: {run_response.text[:500]}"
                )

            result = run_response.json()
            return self._parse_response(result, latency_ms)

        except requests.exceptions.Timeout:
            latency_ms = (time.time() - start_time) * 1000
            return AgentResponse(
                answer="",
                tool_calls=0,
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                latency_ms=latency_ms,
                success=False,
                error="Request timeout"
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return AgentResponse(
                answer="",
                tool_calls=0,
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                latency_ms=latency_ms,
                success=False,
                error=str(e)
            )

    def _parse_response(self, result: dict, latency_ms: float) -> AgentResponse:
        """Parse the LangGraph response to extract metrics."""
        messages = result.get("messages", [])
        tool_calls = 0
        answer = ""
        input_tokens = 0
        output_tokens = 0

        # Extract answer from the last assistant message
        for msg in reversed(messages):
            if isinstance(msg, dict):
                role = msg.get("type") or msg.get("role", "")
                if role in ["ai", "assistant"]:
                    content = msg.get("content", "")
                    if content and isinstance(content, str):
                        answer = content
                        break

        # Count tool calls
        for msg in messages:
            if isinstance(msg, dict):
                msg_type = msg.get("type", "")
                # Count tool messages
                if msg_type == "tool":
                    tool_calls += 1
                # Count tool_calls in AI messages
                if msg.get("tool_calls"):
                    tool_calls += len(msg.get("tool_calls", []))

                # Extract token usage if available
                usage = msg.get("usage_metadata") or msg.get("response_metadata", {}).get("usage", {})
                if usage:
                    input_tokens += usage.get("input_tokens", 0) or usage.get("prompt_tokens", 0)
                    output_tokens += usage.get("output_tokens", 0) or usage.get("completion_tokens", 0)

        return AgentResponse(
            answer=answer,
            tool_calls=tool_calls,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            latency_ms=latency_ms,
            success=True,
            raw_messages=messages
        )

    def health_check(self) -> bool:
        """Check if the LangGraph server is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/ok", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def list_assistants(self) -> list:
        """List available assistants/graphs."""
        try:
            response = self.session.post(
                f"{self.base_url}/assistants/search",
                json={},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []


if __name__ == "__main__":
    # Quick test
    client = LangGraphClient()

    print("Health check:", client.health_check())
    print("\nAvailable assistants:")
    for assistant in client.list_assistants():
        print(f"  - {assistant.get('graph_id', assistant.get('assistant_id', 'unknown'))}")

    print("\nTesting hybrid_rag_agent...")
    response = client.invoke("hybrid_rag_agent", "What is the attention mechanism?")
    print(f"Success: {response.success}")
    print(f"Latency: {response.latency_ms:.2f}ms")
    print(f"Tool calls: {response.tool_calls}")
    print(f"Tokens: {response.total_tokens}")
    print(f"Answer: {response.answer[:200]}...")
