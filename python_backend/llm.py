"""
llm_extraction.py
------------------
Calls Groq's LLM API to extract structured lab metrics from the
filtered OCR text produced by extraction.py.

Install:
    pip install groq --break-system-packages

Requires an API key set as an environment variable:
    export GROQ_API_KEY="your-key-here"
"""

from __future__ import annotations

import json, os
from dotenv import load_dotenv 
from groq import Groq

load_dotenv()
MODEL = "openai/gpt-oss-120b"  # good accuracy/speed balance on free tier

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

EXTRACTION_PROMPT = """You are a medical report extraction assistant.
 
You will be given raw OCR'd text from a patient's lab report. Extract
ONLY the values that are explicitly present in the text. Do not infer,
guess, or fill in values that are not written in the report.
 
Return ONLY valid JSON (no markdown, no commentary) in this exact shape.
IMPORTANT: write "summary" and "risk_score" FIRST, before "metrics" -
the metrics list can be long, and summary/risk_score must never be
dropped because of that:
 
{{
  "summary": "one or two plain-language sentences describing the overall picture",
  "risk_score": number between 0 and 1,
  "metrics": [
    {{
      "name": "string, e.g. Glucose",
      "value": number,
      "unit": "string, e.g. mg/dL",
      "reference_range": "string, e.g. 70-99",
      "flag": "normal" | "high" | "low" | "unknown"
    }}
  ]
}}

Report text:
---
{report_text}
---
"""


def extract_metrics(report_text: str) -> dict:
    """
    Send filtered report text to Groq and parse the structured JSON
    response. Raises ValueError if the model doesn't return valid JSON.
    """
    prompt = EXTRACTION_PROMPT.format(report_text=report_text)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,  # low temperature - we want consistent extraction, not creativity
        response_format={"type": "json_object"},  # forces valid JSON output
    )

    raw = response.choices[0].message.content

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {raw}") from e

def answer_question(report_text: str, question: str) -> str:
    prompt = f"""You are a medical report assistant. Using ONLY the report
text below, answer the user's question in plain language. If the answer
isn't in the report, say so clearly rather than guessing.

Report text:
---
{report_text}
---

Question: {question}
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=512,
    )
    return response.choices[0].message.content

# ---------------------------------------------------------------------------
# Quick manual test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python llm_extraction.py <path_to_text_file>")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        text = f.read()

    result = extract_metrics(text)
    print(json.dumps(result, indent=2))