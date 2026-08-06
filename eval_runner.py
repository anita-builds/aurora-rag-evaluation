"""
eval_runner.py – run Aurora over all eval cases and log results.

Input:
    evals/hr_eval_cases.csv  with columns:
        id,question,expected_phrase[,expected_type]

Output:
    evals/hr_eval_results.csv with columns:
        id,question,expected_phrase,expected_type,answer,passed,
        latency_ms,input_tokens,output_tokens
"""

import csv
import os
import time

from app import answer_hr_question  # app.py must be in the same folder

# Paths to input and output CSV files
CASES_PATH = os.path.join("evals", "hr_eval_cases.csv")
RESULTS_PATH = os.path.join("evals", "hr_eval_results.csv")


def run_eval() -> None:
    # Read input cases
    rows_in: list[dict] = []
    with open(CASES_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows_in.append({
                "id": (row.get("id") or "").strip(),
                "question": (row.get("question") or "").strip(),
                "expected_phrase": (row.get("expected_phrase") or "").strip(),
                "expected_type": (row.get("expected_type") or "").strip()
                               if "expected_type" in reader.fieldnames
                               else "",
            })

    results: list[dict] = []

    for row in rows_in:
        case_id = row["id"]
        question = row["question"]
        expected = row["expected_phrase"]
        expected_type = row["expected_type"]

        if not question:
            continue  # skip empty rows

        print(f"\n=== Case {case_id or '(no id)'} ===")
        print(f"Q: {question}")
        if expected:
            print(f"Expected phrase: {expected!r} (type={expected_type})")
        else:
            print(f"Expected phrase: <none> (type={expected_type})")

        # Time the call – we could also rely on app.py's own timing,
        # but this keeps eval_runner self-contained.
        t0 = time.perf_counter()
        answer_text, input_tokens, output_tokens = answer_hr_question(question)
        dt = time.perf_counter() - t0
        latency_ms = dt * 1000.0

        # Simple pass/fail: expected_phrase substring (case-insensitive)
        if expected:
            passed = expected.lower() in answer_text.lower()
        else:
            # If no expected phrase, treat as pass or handle separately
            passed = True

        print(f"[metrics] latency_ms={latency_ms:.1f}  input_tokens={input_tokens}  output_tokens={output_tokens}")
        print(f"[pass] {passed}")
        print(f"[answer]\n{answer_text}\n")

        results.append({
            "id": case_id,
            "question": question,
            "expected_phrase": expected,
            "expected_type": expected_type,
            "answer": answer_text,
            "passed": str(passed),
            "latency_ms": f"{latency_ms:.1f}",
            "input_tokens": str(input_tokens),
            "output_tokens": str(output_tokens),
        })

    # Write out the results CSV (overwrite on each run)
    fieldnames = [
        "id",
        "question",
        "expected_phrase",
        "expected_type",
        "answer",
        "passed",
        "latency_ms",
        "input_tokens",
        "output_tokens",
    ]

    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)

    with open(RESULTS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


if __name__ == "__main__":
    run_eval()
