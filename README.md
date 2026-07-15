# Lead_scoring_LLM
helps sales reps prioritize inbound leads
# AI Lead Triage Tool

A small Python tool that uses the Claude API to read raw, messy CRM lead
notes and turn them into a prioritized, actionable list for a sales rep.

## The problem

Inbound leads (from web forms, trade shows, referrals, cold outreach) come
in with inconsistent, freeform notes. Reps waste time re-reading every lead
top-to-bottom to figure out what's actually worth calling first. This tool
automates the first pass of that triage.

## What it does

Given a CSV of leads (name, company, source, notes), the script:
- Summarizes each lead in one sentence
- Classifies it as **hot / warm / cold** based on buying-intent signals
  (budget, timeline, decision-making authority, referral strength)
- Flags missing information or red flags
- Outputs a new CSV sorted hot → warm → cold, ready to hand to a rep

## Example output

| name | company | priority | summary | missing_info |
|---|---|---|---|---|
| Priya Patel | Alderbrook Logistics | hot | VP of Sales with approved Q3 budget, wants a call this week | none |
| Lauren Ashby | Vantage Health Systems | hot | Manages 15-person team, contract renewal in 2 months, requested pricing | none |
| Dana Whitfield | BrightPath Education | warm | Strong engagement signals but no direct contact yet | no direct conversation yet |
| Mike Torres | (unknown) | cold | Grabbed brochure, no real budget or intent | no company, vague budget |

## Setup

```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key-here"
```

## Usage

```bash
python triage_leads.py sample_leads.csv triaged_leads.csv
```

## What I learned

- Structuring a prompt to reliably return parseable JSON from an LLM
- Defensive parsing for real-world messy model output
- Applying an AI classification step inside a familiar sales-ops workflow
  (lead sorting) rather than treating AI as a novelty

## Possible improvements

- Batch multiple leads per API call to reduce cost/latency
- Add a confidence score alongside priority
- Connect directly to a CRM export instead of a static CSV
