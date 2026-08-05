"""
app.py - Aurora HR policy assistant

A retrieval-augmented generation (RAG) assistant that answers questions
about a UK Civil Service maternity and shared parental leave policy
booklet, grounded strictly in the retrieved policy text.

- Splits the policy document into paragraph-level chunks
- Scores and retrieves the top-k most relevant chunks per question
  using keyword overlap (see retrieve_paragraphs())
- Answers only from retrieved context, with a defined escalation
  response when the policy does not cover the question
- Logs latency and token usage for every call

See eval_runner.py for the evaluation harness that runs this against
a fixed set of test cases.
"""

import os
import time

from anthropic import Anthropic
from pypdf import PdfReader

# 1. Set up the Anthropic client from the API key in the environment

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# 2. System prompt (multi-line string)

SYSTEM_PROMPT = """
You are Aurora's HR assistant for UK Civil Service maternity and parental leave.

You must answer only using the information provided in the policy context.
Do not rely on outside knowledge, assumptions, or general legal guidance,
even if you think it might be correct. If you cannot find explicit support
in the policy text for the answer, do not guess.

If the policy text does not clearly cover the user's question, say once:
"I’m not certain from the policy text provided. I will escalate this to HR
for further guidance."
Do not repeat that something is not covered.

When the policy text does contain the answer:
- State the rules and entitlements directly as facts, as if speaking on
  behalf of Aurora.
- Never refer to "the document", "the PDF", "the policy document", or
  "the material/sections provided". Instead, say things like:
  "You are entitled to 52 weeks of maternity leave..." rather than
  "The document says you are entitled..."

For questions you cannot and should not help with (for example where the
user asks for dishonest, unsafe or harmful actions), clearly decline to help.
You can say things like "I can't help you with that" and, where appropriate,
advise them to speak to HR or a professional support service.

Always be clear, factual and supportive.
"""

# 3. Load Aurora's maternity policy from the HMG PDF

def load_policy_text() -> str:
    """
    Load text from the HMG maternity policy PDF.

    For v1 we take a simple approach:
    - read all pages
    - extract text from each
    - join them into one big string

    Later we could:
    - clean headers/footers
    - chunk into paragraphs
    - build a smarter retriever
    """
    pdf_path = "data/policies/SPL_Having_a_baby_HMG_Issue_2.pdf"

    reader = PdfReader(pdf_path)
    all_pages_text = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            all_pages_text.append(page_text)

    full_text = "\n\n".join(all_pages_text)
    return full_text

POLICY_TEXT = load_policy_text()

# Split the policy into rough paragraphs for retrieval
POLICY_PARAGRAPHS = [
    p.strip()
    for p in POLICY_TEXT.split("\n\n")
    if p.strip()
]

def retrieve_paragraphs(question: str, top_k: int = 5) -> list[str]:
    """
    Very simple keyword-based retriever:
    - splits the question into words
    - scores each paragraph by how many question words it contains
    - returns the top_k paragraphs by score
    """
    q_words = [w for w in question.lower().split() if len(w) > 3]  # ignore very short words
    scored: list[tuple[int, str]] = []

    for para in POLICY_PARAGRAPHS:
        text_lower = para.lower()
        score = sum(1 for w in q_words if w in text_lower)
        if score > 0:
            scored.append((score, para))

    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        # Fallback: if nothing matched, just return the first top_k paragraphs
        return POLICY_PARAGRAPHS[:top_k]

    return [para for _, para in scored[:top_k]]

def answer_hr_question(question: str) -> str:
    """
    Minimal RAG version:
    - Retrieve top-K relevant paragraphs from the policy
    - Combine them with the question into a user message
    - Call Claude and return the answer text
    """

    chunks = retrieve_paragraphs(question, top_k=5)
    context = "\n\n---\n\n".join(chunks)

    user_message = f"""
Here is some information from Aurora's maternity policy:

{context}

Employee question: {question}

Please answer using ONLY the information in the policy text above.
If the question cannot be answered from that text, say you will escalate to HR.
"""

    # Measure latency
    t0 = time.perf_counter()

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message}
        ],
    )

    dt = time.perf_counter() - t0

        # Extract the text from the first content block
    answer_text = response.content[0].text

    # Extract token usage (for metrics / cost calculations)
    usage = getattr(response, "usage", None)
    if usage is not None:
        input_tokens = getattr(usage, "input_tokens", 0) or 0
        output_tokens = getattr(usage, "output_tokens", 0) or 0
    else:
        input_tokens = 0
        output_tokens = 0

    # Log a simple line so we can see what's happening in interactive mode
    print(f"[metrics] latency_ms={dt * 1000:.1f}  input_tokens={input_tokens}  output_tokens={output_tokens}")

    # In eval mode we may want to get the tokens as well,
    # so return them alongside the answer text.
    return answer_text, input_tokens, output_tokens

if __name__ == "__main__":
    print("Aurora HR helper – minimal demo")
    print("Type a question about maternity leave (or 'quit' to exit).")
    while True:
        q = input("\nYou: ").strip()
        if not q or q.lower() in ("q", "quit", "exit"):
            break
        answer_text, _, _ = answer_hr_question(q)
        print("\nAssistant:", answer_text)


