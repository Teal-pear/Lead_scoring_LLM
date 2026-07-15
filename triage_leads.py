"""
AI Lead Triage Tool
--------------------
Reads a CSV of raw CRM leads, uses the Claude API to summarize and
prioritize each one, and writes out a sorted CSV ready for a sales
rep to act on.

Setup:
    pip install anthropic
    export ANTHROPIC_API_KEY="your-key-here"

Usage:
    python triage_leads.py sample_leads.csv triaged_leads.csv
"""

import csv
import json
import sys
import time

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are a sales operations assistant that triages inbound CRM leads.

For each lead, you will be given: name, company, source, and freeform notes.

Return ONLY a JSON object (no markdown, no preamble) with these exact keys:
{
  "summary": "one sentence, plain language summary of the lead",
  "priority": "hot" | "warm" | "cold",
  "missing_info": "short note on what's missing or a red flag, or 'none' if the lead looks complete",
  "reasoning": "one short phrase on why you assigned this priority"
}

Priority guidance:
- "hot": clear buying intent, budget/timeline mentioned, decision-maker, or strong referral
- "warm": genuine interest or engagement, but missing budget, timeline, or authority info
- "cold": no real intent signals, explicit disinterest, unqualified (e.g. student/intern research), or missing basic info
"""


def classify_lead(lead: dict) -> dict:
    """Call the Claude API to classify a single lead. Returns a dict."""
    user_content = (
        f"Name: {lead.get('name', '')}\n"
        f"Company: {lead.get('company', '') or '(not provided)'}\n"
        f"Source: {lead.get('source', '')}\n"
        f"Notes: {lead.get('notes', '')}"
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    raw_text = response.content[0].text.strip()

    # Defensive parsing in case the model wraps output in markdown fences
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.lower().startswith("json"):
            raw_text = raw_text[4:].strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "summary": "(could not parse model output)",
            "priority": "warm",
            "missing_info": "parsing error - review manually",
            "reasoning": raw_text[:100],
        }


def main(input_path: str, output_path: str):
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        leads = list(reader)

    print(f"Loaded {len(leads)} leads from {input_path}")

    results = []
    for i, lead in enumerate(leads, start=1):
        print(f"  Classifying lead {i}/{len(leads)}: {lead.get('name', 'unknown')}...")
        classification = classify_lead(lead)
        merged = {**lead, **classification}
        results.append(merged)
        time.sleep(0.3)  # gentle pacing, not required but polite to the API

    # Sort: hot first, then warm, then cold
    priority_order = {"hot": 0, "warm": 1, "cold": 2}
    results.sort(key=lambda r: priority_order.get(r.get("priority", "warm"), 1))

    fieldnames = list(leads[0].keys()) + ["summary", "priority", "missing_info", "reasoning"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDone. Wrote sorted results to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python triage_leads.py <input_csv> <output_csv>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
