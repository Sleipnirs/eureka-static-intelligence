---
name: Eureka-Static-Intelligence
version: 0.1.0
type: executable-skill
tier: standard
category: dev-environment
summary: Compile a standardized enterprise FAQ list + industry vocabulary into a self-contained static-intelligence chatbox — one HTML file, no LLM, no backend, conversationally robust.
entrypoint: main.py
license: MIT
generator: Eureka Group
---

# Eureka-Static-Intelligence

## What this skill does

Turns any enterprise's FAQ knowledge into a chatbox that FEELS like strong AI
is behind it — while nothing but frozen, verifiable, static intelligence runs
inside. The conversational robustness (paraphrase matching, typo tolerance,
bilingual bridging, small-talk handling, context threading, graceful AEO
hand-off) is distilled from FinChip Generator v3.0's five-layer lexical
engine and compiled INTO the output file.

## Quick reference

| Field | Value |
|---|---|
| Input | One JSON: ① FAQ list (≥10, 100 recommended) ② industry vocabulary ③ optional task flow |
| Output | `out/<brand>-chatbox.html` — self-contained, host anywhere, iframe anywhere |
| Runtime deps | None. Python 3.10+ stdlib to compile; plain browser to run |
| Intelligence | 100% static: keyword + token-overlap + synonyms + char-ngram TF-IDF cosine + context priors |
| Cost per query | Zero. Forever. |

## The compiler does the craft for you

- **Auto keywords** — distinctive tokens per question (corpus tf-idf), with
  prefix variants so "cancel" finds "cancellation"
- **Auto topic threads** — top-2 similar nodes (n-gram cosine) become each
  answer's follow-up chips: conversations walk, they don't dead-end
- **Auto Quick-10** — `"mainline": true` flags win; otherwise centrality ranking
- **Right rail** — Quick-10 always; second panel renders the customer's task
  flow if provided, else the built-in toolbox (calculator · JSON validator ·
  timestamp · unit converter · text stats + SHA-256 · Google-AI search
  hand-off; image tools slot reserved)

## How to run

```bash
python main.py examples/input_dental.json
# → out/sunny-dental-clinic-chatbox.html  (~47 KB, ready to ship)
```

Input format: see INPUT-FORMAT.md. The dental-clinic example doubles as a
template — copy it, replace brand/faq/vocab, recompile.

## Conversational behaviors compiled into every output

Three-chip discipline (thread + quick + brand anchor) · exploration-depth
chip policy · visited-set anti-loop walking · connective phrasing on same
thread · anti-repeat penalty on pronoun follow-ups · ellipsis topic injection
· sentence-level sentiment (700+ term small talk, extendable per industry) ·
inline calculator on typed expressions · did-you-mean clarification tier ·
soft-landing external AI search card. Bilingual (en/zh) when the pack is.

## Provenance

First instance of the Static Intelligence class. Reference implementation
parameters were proofed on FinChip Generator v3.0 (finchip.ai/generator).

## Disclaimer

Informational only. Answers are exactly as good as the FAQ pack you compile.
