"""
LLM-as-Judge Evaluator for RAG Answer Correctness

Uses the same LLM (Qwen) to evaluate answer correctness against ground truth.
Scores answers on a 1-5 scale with explanations.
"""

import os
import json
import re
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


JUDGE_SYSTEM_PROMPT = """You are an expert evaluator for RAG (Retrieval-Augmented Generation) systems.
Your task is to evaluate how well a system's answer matches the expected ground truth answer.

Be fair and objective. Focus on factual correctness and completeness."""

JUDGE_USER_PROMPT = """Evaluate the following RAG system answer against the ground truth.

## Question
{question}

## Ground Truth Answer (Expected)
{ground_truth}

## System Answer (To Evaluate)
{answer}

## Evaluation Criteria
Score the answer on a scale of 1-5:

1 = COMPLETELY WRONG: The answer is factually incorrect, irrelevant, or contradicts the ground truth
2 = MOSTLY WRONG: The answer has major factual errors or misses the main point entirely
3 = PARTIALLY CORRECT: The answer captures some correct information but has significant omissions or minor errors
4 = MOSTLY CORRECT: The answer is factually correct with only minor omissions or slight inaccuracies
5 = FULLY CORRECT: The answer is accurate, complete, and matches or exceeds the ground truth quality

## Important Notes
- Focus on FACTUAL CORRECTNESS, not writing style
- Partial credit is acceptable - a correct but incomplete answer can still score 3-4
- The system answer doesn't need to be word-for-word identical to ground truth
- Consider semantic equivalence (same meaning = correct)

## Response Format
Return your evaluation as a JSON object with exactly these fields:
{{"score": <integer 1-5>, "explanation": "<your reasoning in 1-2 sentences>"}}

Return ONLY the JSON object, no other text."""


@dataclass
class JudgeResult:
    """Result from LLM judge evaluation."""
    score: int  # 1-5
    explanation: str
    success: bool
    error: Optional[str] = None


class LLMJudge:
    """LLM-as-Judge for evaluating RAG answer correctness."""

    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        api_key: str = None,
        temperature: float = 0.1  # Low temperature for consistent scoring
    ):
        """
        Initialize the LLM Judge.

        Args:
            base_url: OpenAI-compatible API endpoint
            model: Model name to use
            api_key: API key (can be placeholder for local models)
            temperature: Sampling temperature (low for consistency)
        """
        self.base_url = base_url or os.getenv("LLM_BASE_URL", "http://10.26.1.56:8708/v1")
        self.model = model or os.getenv("LLM_MODEL", "Qwen/Qwen3-235B-A22B-Instruct-2507-FP8")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "sk-placeholder")
        self.temperature = temperature

        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

    def evaluate(self, question: str, ground_truth: str, answer: str) -> JudgeResult:
        """
        Evaluate an answer against ground truth.

        Args:
            question: The original question
            ground_truth: The expected correct answer
            answer: The system's answer to evaluate

        Returns:
            JudgeResult with score (1-5) and explanation
        """
        if not answer or not answer.strip():
            return JudgeResult(
                score=1,
                explanation="No answer provided by the system",
                success=True
            )

        prompt = JUDGE_USER_PROMPT.format(
            question=question,
            ground_truth=ground_truth,
            answer=answer
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=500
            )

            content = response.choices[0].message.content.strip()
            return self._parse_response(content)

        except Exception as e:
            return JudgeResult(
                score=0,
                explanation="",
                success=False,
                error=str(e)
            )

    def _parse_response(self, content: str) -> JudgeResult:
        """Parse the LLM's JSON response."""
        try:
            # Try to extract JSON from the response
            # Handle cases where model might add extra text
            json_match = re.search(r'\{[^{}]*"score"[^{}]*"explanation"[^{}]*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group()

            # Clean up common issues
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            result = json.loads(content)
            score = int(result.get("score", 0))
            explanation = str(result.get("explanation", ""))

            # Validate score range
            if score < 1 or score > 5:
                score = max(1, min(5, score))

            return JudgeResult(
                score=score,
                explanation=explanation,
                success=True
            )

        except json.JSONDecodeError:
            # Try to extract score from text if JSON parsing fails
            score_match = re.search(r'["\']?score["\']?\s*:\s*(\d)', content)
            if score_match:
                score = int(score_match.group(1))
                return JudgeResult(
                    score=max(1, min(5, score)),
                    explanation=f"Extracted from: {content[:100]}...",
                    success=True
                )

            return JudgeResult(
                score=0,
                explanation="",
                success=False,
                error=f"Failed to parse JSON response: {content[:200]}"
            )


class BatchJudge:
    """Batch evaluation helper for multiple question-answer pairs."""

    def __init__(self, judge: LLMJudge = None):
        self.judge = judge or LLMJudge()

    def evaluate_batch(self, evaluations: list) -> list:
        """
        Evaluate a batch of question-answer pairs.

        Args:
            evaluations: List of dicts with keys: question, ground_truth, answer

        Returns:
            List of JudgeResult objects
        """
        results = []
        for i, eval_item in enumerate(evaluations):
            print(f"  Judging {i+1}/{len(evaluations)}...", end="\r")
            result = self.judge.evaluate(
                question=eval_item["question"],
                ground_truth=eval_item["ground_truth"],
                answer=eval_item["answer"]
            )
            results.append(result)
        print()
        return results


if __name__ == "__main__":
    # Quick test
    judge = LLMJudge()

    # Test case 1: Good answer
    result = judge.evaluate(
        question="What is the dimension of the model (dmodel) in the Transformer?",
        ground_truth="The Transformer uses dmodel = 512 as the dimension for all sub-layers and embedding layers.",
        answer="The model dimension dmodel in the Transformer architecture is 512. This is used consistently throughout the encoder and decoder stacks."
    )
    print(f"Test 1 - Good answer:")
    print(f"  Score: {result.score}/5")
    print(f"  Explanation: {result.explanation}")
    print(f"  Success: {result.success}")
    print()

    # Test case 2: Wrong answer
    result = judge.evaluate(
        question="What is the dimension of the model (dmodel) in the Transformer?",
        ground_truth="The Transformer uses dmodel = 512 as the dimension for all sub-layers and embedding layers.",
        answer="The model uses a dimension of 1024 for its embeddings."
    )
    print(f"Test 2 - Wrong answer:")
    print(f"  Score: {result.score}/5")
    print(f"  Explanation: {result.explanation}")
    print(f"  Success: {result.success}")
