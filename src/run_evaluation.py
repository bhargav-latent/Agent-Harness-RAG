"""
Evaluation Runner for FileSearch RAG

This script runs the evaluation dataset through the FileSearch RAG agent
and measures Correctness, Latency, and Cost.
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

from filesearch_rag import FileSearchRAG

# Load environment variables
load_dotenv()


class RAGEvaluator:
    """Evaluates RAG system performance"""

    def __init__(self, rag_system: FileSearchRAG, output_dir: str = "./evaluation/results"):
        self.rag = rag_system
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_evaluation_dataset(self, dataset_path: str) -> List[Dict]:
        """Load evaluation questions from JSONL file"""
        questions = []
        with open(dataset_path, 'r', encoding='utf-8') as f:
            for line in f:
                questions.append(json.loads(line))
        return questions

    def evaluate_single_question(self, question_data: Dict) -> Dict[str, Any]:
        """Evaluate a single question"""
        question_id = question_data["id"]
        question = question_data["question"]
        ground_truth = question_data["ground_truth"]
        category = question_data["category"]

        print(f"\n{'='*80}")
        print(f"Evaluating {question_id} ({category})")
        print(f"Question: {question}")
        print(f"{'='*80}\n")

        # Measure latency
        start_time = time.time()

        try:
            result = self.rag.query(question)
            latency_ms = (time.time() - start_time) * 1000

            # Prepare result
            evaluation_result = {
                **question_data,  # Include all original fields
                "answer": result["answer"],
                "retrieved_contexts": self._extract_contexts(result.get("intermediate_steps", [])),
                "latency_ms": round(latency_ms, 2),
                "success": result["success"],
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "latency_ms": round(latency_ms, 2),
                    # Note: Correctness and other metrics would be computed separately
                    # using ground_truth comparison (manual or automated)
                }
            }

            print(f"\n✅ Answer generated in {latency_ms:.2f}ms")
            print(f"Answer: {result['answer'][:200]}...")

            return evaluation_result

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            return {
                **question_data,
                "answer": None,
                "error": str(e),
                "latency_ms": (time.time() - start_time) * 1000,
                "success": False,
                "timestamp": datetime.now().isoformat()
            }

    def _extract_contexts(self, intermediate_steps: List) -> List[str]:
        """Extract retrieved contexts from intermediate steps"""
        contexts = []
        for step in intermediate_steps:
            if len(step) >= 2:
                action, observation = step[0], step[1]
                # Extract file reads and search results
                if "read_document" in str(action) or "search" in str(action):
                    if observation and len(observation) > 100:
                        contexts.append(observation[:1000])  # Limit context size
        return contexts

    def run_evaluation(
        self,
        dataset_path: str,
        limit: int = None,
        categories: List[str] = None,
        output_filename: str = None
    ) -> Dict[str, Any]:
        """
        Run evaluation on the dataset

        Args:
            dataset_path: Path to evaluation JSONL file
            limit: Optional limit on number of questions to evaluate
            categories: Optional list of categories to filter
            output_filename: Custom output filename (default: filesearch_results_TIMESTAMP.jsonl)

        Returns:
            Summary statistics
        """
        print(f"\n{'='*80}")
        print("FileSearch RAG Evaluation")
        print(f"{'='*80}\n")

        # Load dataset
        print(f"Loading dataset from: {dataset_path}")
        questions = self.load_evaluation_dataset(dataset_path)
        print(f"Loaded {len(questions)} questions")

        # Filter by categories if specified
        if categories:
            questions = [q for q in questions if q["category"] in categories]
            print(f"Filtered to {len(questions)} questions in categories: {categories}")

        # Limit if specified
        if limit:
            questions = questions[:limit]
            print(f"Limiting to first {limit} questions")

        # Run evaluation
        results = []
        successful = 0
        total_latency = 0

        for i, question_data in enumerate(questions, 1):
            print(f"\n\nProgress: {i}/{len(questions)}")
            result = self.evaluate_single_question(question_data)
            results.append(result)

            if result["success"]:
                successful += 1
                total_latency += result["latency_ms"]

        # Compute statistics
        stats = {
            "total_questions": len(questions),
            "successful": successful,
            "failed": len(questions) - successful,
            "success_rate": round(successful / len(questions) * 100, 2) if questions else 0,
            "avg_latency_ms": round(total_latency / successful, 2) if successful > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }

        # Category breakdown
        category_stats = {}
        for result in results:
            cat = result["category"]
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "successful": 0}
            category_stats[cat]["total"] += 1
            if result["success"]:
                category_stats[cat]["successful"] += 1

        stats["by_category"] = {
            cat: {
                **data,
                "success_rate": round(data["successful"] / data["total"] * 100, 2)
            }
            for cat, data in category_stats.items()
        }

        # Save results
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"filesearch_results_{timestamp}.jsonl"

        output_path = self.output_dir / output_filename
        with open(output_path, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')

        print(f"\n\n{'='*80}")
        print("Evaluation Complete!")
        print(f"{'='*80}")
        print(f"\nResults saved to: {output_path}")
        print(f"\nStatistics:")
        print(f"  Total Questions: {stats['total_questions']}")
        print(f"  Successful: {stats['successful']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Success Rate: {stats['success_rate']}%")
        print(f"  Avg Latency: {stats['avg_latency_ms']:.2f}ms")
        print(f"\nBy Category:")
        for cat, data in stats["by_category"].items():
            print(f"  {cat}: {data['successful']}/{data['total']} ({data['success_rate']}%)")

        return stats


# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run FileSearch RAG evaluation")
    parser.add_argument(
        "--dataset",
        default="./evaluation/datasets/evaluation_set.jsonl",
        help="Path to evaluation dataset JSONL file"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of questions to evaluate (default: all)"
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        default=None,
        help="Filter by categories (e.g., --categories exact_match semantic)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Custom output filename (default: filesearch_results_TIMESTAMP.jsonl)"
    )

    args = parser.parse_args()

    # Initialize RAG system
    print("Initializing FileSearch RAG system...")
    rag = FileSearchRAG()

    # Initialize evaluator
    evaluator = RAGEvaluator(rag)

    # Run evaluation
    stats = evaluator.run_evaluation(
        dataset_path=args.dataset,
        limit=args.limit,
        categories=args.categories,
        output_filename=args.output
    )

    print(f"\n{'='*80}\n")
