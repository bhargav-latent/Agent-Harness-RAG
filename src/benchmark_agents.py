#!/usr/bin/env python3
"""
RAG Agent Benchmark Runner

Benchmarks RAG agents against the evaluation dataset with:
- Latency measurement
- Token usage tracking
- Tool call counting
- LLM-as-judge correctness scoring

Outputs results to CSV for analysis.
"""

import os
import sys
import json
import csv
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.langgraph_client import LangGraphClient, AgentResponse
from src.llm_judge import LLMJudge, JudgeResult


class BenchmarkRunner:
    """Orchestrates benchmark evaluation across RAG agents."""

    def __init__(
        self,
        langgraph_url: str = "http://127.0.0.1:2026",
        output_dir: str = "./evaluation/results"
    ):
        """
        Initialize the benchmark runner.

        Args:
            langgraph_url: URL of the LangGraph server
            output_dir: Directory for output files
        """
        self.client = LangGraphClient(langgraph_url)
        self.judge = LLMJudge()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_dataset(self, dataset_path: str) -> list:
        """Load evaluation dataset from JSONL file."""
        questions = []
        with open(dataset_path, "r") as f:
            for line in f:
                if line.strip():
                    questions.append(json.loads(line))
        return questions

    def run_benchmark(
        self,
        dataset_path: str,
        agents: list = None,
        limit: Optional[int] = None,
        categories: Optional[list] = None,
        skip_judge: bool = False
    ) -> str:
        """
        Run the benchmark evaluation.

        Args:
            dataset_path: Path to evaluation dataset JSONL
            agents: List of agent names to benchmark (default: both)
            limit: Maximum number of questions to evaluate
            categories: Filter to specific categories
            skip_judge: Skip LLM-as-judge evaluation (faster)

        Returns:
            Path to output CSV file
        """
        agents = agents or ["hybrid_rag_agent", "filesearch_agent"]
        questions = self.load_dataset(dataset_path)

        # Filter by category if specified
        if categories:
            questions = [q for q in questions if q.get("category") in categories]

        # Limit questions if specified
        if limit:
            questions = questions[:limit]

        print("=" * 80)
        print("RAG AGENT BENCHMARK")
        print("=" * 80)
        print(f"Dataset: {dataset_path}")
        print(f"Questions: {len(questions)}")
        print(f"Agents: {', '.join(agents)}")
        print(f"LLM Judge: {'Enabled' if not skip_judge else 'Disabled'}")
        print("=" * 80)
        print()

        # Check server health
        if not self.client.health_check():
            print("ERROR: LangGraph server is not responding!")
            print(f"Make sure the server is running at {self.client.base_url}")
            sys.exit(1)

        results = []
        total_evaluations = len(questions) * len(agents)
        current = 0

        for question in questions:
            for agent in agents:
                current += 1
                q_id = question.get("id", "unknown")
                q_text = question.get("question", "")[:50]

                print(f"[{current}/{total_evaluations}] {agent} | {q_id}: {q_text}...")

                # Invoke agent
                response = self.client.invoke(agent, question["question"])

                # Build result record
                result = {
                    "question_id": question.get("id", ""),
                    "question": question.get("question", ""),
                    "category": question.get("category", ""),
                    "difficulty": question.get("metadata", {}).get("difficulty", ""),
                    "agent": agent,
                    "ground_truth": question.get("ground_truth", ""),
                    "answer": response.answer,
                    "latency_ms": round(response.latency_ms, 2),
                    "tool_calls": response.tool_calls,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "total_tokens": response.total_tokens,
                    "success": response.success,
                    "error": response.error or "",
                    "correctness_score": 0,
                    "correctness_explanation": ""
                }

                # Run LLM judge if enabled and agent succeeded
                if not skip_judge and response.success and response.answer:
                    judge_result = self.judge.evaluate(
                        question=question["question"],
                        ground_truth=question["ground_truth"],
                        answer=response.answer
                    )
                    result["correctness_score"] = judge_result.score
                    result["correctness_explanation"] = judge_result.explanation

                results.append(result)

                # Progress indicator
                if response.success:
                    score_str = f"Score: {result['correctness_score']}/5" if not skip_judge else ""
                    print(f"    OK - {response.latency_ms:.0f}ms, {response.tool_calls} tools, {response.total_tokens} tokens {score_str}")
                else:
                    print(f"    FAILED - {response.error}")

        # Save results
        output_path = self._save_results(results, agents)

        # Print summary
        self._print_summary(results, agents)

        return output_path

    def _save_results(self, results: list, agents: list) -> str:
        """Save results to CSV file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"benchmark_{timestamp}.csv"
        output_path = self.output_dir / filename

        # Define CSV columns
        columns = [
            "question_id", "question", "category", "difficulty", "agent",
            "ground_truth", "answer", "latency_ms", "tool_calls",
            "input_tokens", "output_tokens", "total_tokens",
            "success", "error", "correctness_score", "correctness_explanation"
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for result in results:
                # Truncate long fields for CSV readability
                row = result.copy()
                row["question"] = row["question"][:500] if row["question"] else ""
                row["ground_truth"] = row["ground_truth"][:500] if row["ground_truth"] else ""
                row["answer"] = row["answer"][:1000] if row["answer"] else ""
                row["correctness_explanation"] = row["correctness_explanation"][:500] if row["correctness_explanation"] else ""
                writer.writerow(row)

        print(f"\nResults saved to: {output_path}")

        # Also save full results as JSONL for detailed analysis
        jsonl_path = self.output_dir / f"benchmark_{timestamp}.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
        print(f"Full results (JSONL): {jsonl_path}")

        return str(output_path)

    def _print_summary(self, results: list, agents: list):
        """Print benchmark summary statistics."""
        print("\n" + "=" * 80)
        print("BENCHMARK SUMMARY")
        print("=" * 80)

        for agent in agents:
            agent_results = [r for r in results if r["agent"] == agent]
            successful = [r for r in agent_results if r["success"]]

            print(f"\n{agent.upper()}")
            print("-" * 40)
            print(f"  Total Questions: {len(agent_results)}")
            print(f"  Successful: {len(successful)} ({100*len(successful)/len(agent_results):.1f}%)")

            if successful:
                avg_latency = sum(r["latency_ms"] for r in successful) / len(successful)
                avg_tools = sum(r["tool_calls"] for r in successful) / len(successful)
                avg_tokens = sum(r["total_tokens"] for r in successful) / len(successful)
                avg_score = sum(r["correctness_score"] for r in successful) / len(successful)

                print(f"  Avg Latency: {avg_latency:.0f}ms")
                print(f"  Avg Tool Calls: {avg_tools:.1f}")
                print(f"  Avg Tokens: {avg_tokens:.0f}")
                print(f"  Avg Correctness Score: {avg_score:.2f}/5")

                # Score distribution
                scores = [r["correctness_score"] for r in successful if r["correctness_score"] > 0]
                if scores:
                    print(f"  Score Distribution:")
                    for s in range(1, 6):
                        count = scores.count(s)
                        pct = 100 * count / len(scores) if scores else 0
                        bar = "#" * int(pct / 5)
                        print(f"    {s}: {count:3d} ({pct:5.1f}%) {bar}")

        # Category breakdown
        print(f"\nPERFORMANCE BY CATEGORY")
        print("-" * 40)

        categories = sorted(set(r["category"] for r in results))
        for category in categories:
            cat_results = [r for r in results if r["category"] == category and r["success"]]
            if cat_results:
                avg_score = sum(r["correctness_score"] for r in cat_results) / len(cat_results)
                print(f"  {category}: {avg_score:.2f}/5 (n={len(cat_results)})")

        print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Benchmark RAG agents")
    parser.add_argument(
        "--dataset",
        default="./evaluation/datasets/evaluation_set.jsonl",
        help="Path to evaluation dataset"
    )
    parser.add_argument(
        "--agents",
        nargs="+",
        default=["hybrid_rag_agent", "filesearch_agent"],
        help="Agents to benchmark"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of questions"
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        default=None,
        help="Filter by categories"
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:2026",
        help="LangGraph server URL"
    )
    parser.add_argument(
        "--output",
        default="./evaluation/results",
        help="Output directory"
    )
    parser.add_argument(
        "--skip-judge",
        action="store_true",
        help="Skip LLM-as-judge evaluation"
    )

    args = parser.parse_args()

    runner = BenchmarkRunner(
        langgraph_url=args.url,
        output_dir=args.output
    )

    runner.run_benchmark(
        dataset_path=args.dataset,
        agents=args.agents,
        limit=args.limit,
        categories=args.categories,
        skip_judge=args.skip_judge
    )


if __name__ == "__main__":
    main()
