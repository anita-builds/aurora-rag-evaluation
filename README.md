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
- Policy source used during development (public):
  https://assets.publishing.service.gov.uk/media/6a4e187c92f65594cb0299bd/SPL_Having_a_baby_HMG_2026v0c.pdf
  
## How to Run

Requires Python 3.10+ and an Anthropic API key. Run all commands below
from the repository's root folder.
1. Install dependencies:
   pip install -r requirements.txt
2. Set your Anthropic API key as an environment variable:
   export ANTHROPIC_API_KEY=your-key-here
3. Download the policy PDF linked above and save it to:
   data/policies/SPL_Having_a_baby_HMG_Issue_2.pdf
4. Run the assistant interactively:
   python app.py


