# Evaluation overview

## Goal
Improve reliability by ensuring the assistant:
1) answers only when policy support exists
2) escalates clearly when policy is silent or ambiguous
3) responds consistently across paraphrases

## Test coverage
The test set covers:
- direct policy questions
- edge cases and ambiguous phrasing
- policy-silent questions that should escalate
- safety and privacy handling

Each case includes:
- question
- expected behaviour category
- notes on what “good” looks like

## What is measured
- groundedness
- escalation correctness
- consistency
- operational signals such as latency and token usage where available

## Iteration loop
1) run tests
2) identify failure modes
3) adjust prompts, rules, and retrieval settings
4) rerun and compare changes
