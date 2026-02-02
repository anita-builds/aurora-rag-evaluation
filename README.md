# Aurora: RAG and evaluation notes

Aurora is an applied AI project exploring how to make a policy-grounded assistant reliable in a real setting. The focus is on grounded answers, clear escalation when policy is silent, and repeatable evaluation.

This repository is a sanitised overview intended to demonstrate evaluation thinking, troubleshooting mindset, and documentation quality.

## What this demonstrates
- Retrieval-augmented generation with paragraph chunking and top-k retrieval
- Prompt constraints to answer from retrieved policy content
- Escalation rules when policy does not cover a question
- A repeatable evaluation harness and iteration loop
- Operational instrumentation, including latency and token tracking

## Contents
- `EVALS_OVERVIEW.md` – how tests are structured, what is measured, and how iterations are run
- `ROADMAP.md` – practical next improvements to increase reliability
- `samples/test_cases_template.csv` – a simple test case template

## Notes
- This repo does not include any sensitive source policy documents.
- Policy source used during development (public): https://assets.publishing.service.gov.uk/media/66ea893ee4b40ed591881cc2/2024-08-14_SPL_Having_a_baby_HMG_Issue_2.pdf


