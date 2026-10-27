# Telecom Concierge — LangSmith Workshop

An instructor-led LangSmith workshop built around **Northwind Mobile**, a fictional telecom
customer-support concierge (a `deepagents` deep agent). Module 01 covers **Traces & Threads**.

> All customer data is synthetic. Northwind Mobile is fictional — not affiliated with any real carrier.

## Setup
```bash
uv sync --extra dev
cp .env.example .env     # fill in LANGSMITH_API_KEY (covers tracing + Context Hub + model gateway)
uv run python scripts/setup_context_hub.py   # seed skills + instructions to Context Hub
uv run jupyter notebook modules/01_traces_and_threads.ipynb
```

## Try the agent live
```bash
uv run langgraph dev
```

## Layout
- `agents/telecom_concierge.py` — the deep agent (tools, subagent, hub-pulled skills/instructions)
- `agents/deployable/` — deployable graph + seed `AGENTS.md` + `skills/`
- `utils/` — models, config (per-user project), mock data, Context Hub, seeding
- `modules/01_traces_and_threads.ipynb` — the workshop notebook
- `modules/02_online_evals.ipynb` — online evaluators (set up in LangSmith) + seeding to score them
- `modules/03_offline_evals.ipynb` — datasets + experiments (final-response / single-step / trajectory) + A/B prompt versions from Context Hub

## Note on intentional defects
The hub `AGENTS.md` and `get_customer_account` tool deliberately cause hallucination and PII
leakage to populate failure-mode traces for later modules. These are intentional demo artifacts.
