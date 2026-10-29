# Telecom Concierge — LangSmith Workshop

An instructor-led LangSmith workshop built around **Northwind Mobile**, a fictional telecom
customer-support concierge. We will trace both langchain, non-langchain, and general OTEL agents, then follow a [`deepagents`](https://github.com/langchain-ai/deepagents)
deep agent — tools, a subagent, and skills — using the five notebooks walk through the full agent
engineering loop in LangSmith: **trace → evaluate (online & offline) → find failures → review**.

> All customer data is synthetic. Northwind Mobile is fictional — not affiliated with any real carrier.
> The agent ships with an **intentional defect** (it reads back PII) so the
> failure-mode and evaluation modules have something real to catch.

---

## File structure

```
telecom-concierge/
├── README.md
├── pyproject.toml                     # uv project + dependencies
├── .env.example                       # copy to .env and fill in
├── langgraph.json                     # registers the deployable graph for `langgraph dev`
│
├── agents/
│   ├── telecom_concierge.py           # the deep-agent builder: tools, network-diagnostics subagent,
│   │                                  #   instructions + skills pulled from Context Hub (local fallback)
│   └── deployable/
│       ├── agent.py                   # module-level graph referenced by langgraph.json
│       ├── AGENTS.md                  # seed instructions (the "buggy" copy also pushed to Context Hub)
│       └── skills/                    # SKILL.md sources: bill-explainer, plan-comparison, outage-triage
│
├── utils/
│   ├── models.py                      # model init — provider key + optional gateway (see below)
│   ├── config.py                      # per-user project naming, load_active_agent(), persist_project()
│   ├── mock_data.py                   # synthetic customers (with fake PII), plans, support-doc KB
│   ├── context_hub.py                 # push/pull skills, instructions, and A/B prompt variants
│   ├── seeding.py                     # categorized prompts + trace/thread seeding helpers
│   ├── langsmith_rules.py             # run-rule + annotation-queue helpers (online evals, routing)
│   └── evaluators.py                  # shared evaluator output schema
│
├── scripts/
│   ├── setup_context_hub.py           # one-shot: push skills + instructions to Context Hub
│   └── make_sample_bill.py            # generate assets/sample_bill.png (multimodal demo)
│
├── assets/sample_bill.png             # image used in the multi-modal tracing example
├── images/                            # screenshots embedded in the UI-walkthrough modules
├── tests/                             # pytest: config, mock_data, tools, seeding
└── modules/                           # the five workshop notebooks (run in order)
```

---

## Setup

**Prerequisites:** Python 3.11+, [`uv`](https://docs.astral.sh/uv/), a LangSmith account, and a model
provider key (Anthropic by default).

```bash
uv sync --extra dev                           # install deps (incl. pytest)
cp .env.example .env                          # then edit .env — see keys below
uv run python scripts/setup_context_hub.py    # push the agent's skills + instructions to Context Hub
uv run jupyter notebook modules/01_traces_and_threads.ipynb
```

### Environment variables (`.env`)

| Key | Required | Purpose |
|---|---|---|
| `LANGSMITH_API_KEY` | ✅ | Tracing, Context Hub, datasets/experiments, online evals |
| `LANGSMITH_TRACING` | ✅ | Set to `true` to capture traces |
| `LANGSMITH_ENDPOINT` | — | LangSmith API base — cloud default `https://api.smith.langchain.com`; **set to your instance URL if self-hosted** |
| `ANTHROPIC_API_KEY` | ✅ | The model provider key (default provider) |
| `MODEL_BASE_URL` | — | *Optional* — route model calls through **your own gateway** (see below) |
| `MODEL_NAME` | — | *Optional* — override the model (default `claude-sonnet-4-6`) |

`.env` is git-ignored — your keys never get committed. `.env.example` is the committed template.

**Self-hosted LangSmith:** set `LANGSMITH_ENDPOINT` to your instance URL. Everything derives from it —
tracing, Context Hub, datasets/experiments (via the SDK `Client`), and the OTEL endpoints in Module 1 are
all built from `LANGSMITH_ENDPOINT`, so nothing is hardcoded to the cloud host.

Each attendee's traces, datasets, and experiments are **namespaced by name** (`telecom-concierge-<you>`),
so a shared workspace doesn't collide — the notebooks prompt for your name and set the project for you.

---

## Model options & gateway

All model configuration lives in **`utils/models.py`** (the single source of truth — swap providers or
endpoints there, no notebook edits needed).

- **Default — Anthropic direct.** Uses `ANTHROPIC_API_KEY` with `claude-sonnet-4-6` (vision-capable, which
  the multi-modal tracing example needs).
- **Your own gateway (optional).** Set `MODEL_BASE_URL` to any Anthropic-compatible proxy/gateway endpoint;
  the same `ANTHROPIC_API_KEY` is sent as the credential against it. Leave it unset to call Anthropic
  directly. This keeps the repo **gateway-agnostic** — point it at your org's gateway, or don't.
- **Different model.** Set `MODEL_NAME` (e.g. a different Claude snapshot).
- **Other providers.** Edit `utils/models.py` to use a different `init_chat_model(...)` provider string.

`utils/models.py` also exposes `anthropic_client_args()` so the Strands and OpenTelemetry examples in
Module 1 use the exact same provider/gateway configuration as the main agent.

---

## Try the agent live

```bash
uv run langgraph dev          # opens LangGraph Studio against the telecom_concierge graph
```

Run the **"Your project"** cell in a notebook first — it writes `LANGSMITH_PROJECT` to `.env` so the
separate `langgraph dev` process traces into the same project. Restart `langgraph dev` if it's already up.

---

## The modules

Run in order — each builds on the traces/evaluators/datasets the previous ones produced.

### `01_traces_and_threads.ipynb` — Traces & Threads
- The minimal recipe: tracing LangChain / LangGraph / Deep Agents is automatic (just env vars — no code).
- Per-user project; seed 5 traces (distinct shapes) and multi-turn **threads**.
- A **multi-modal** attachment (a bill image) rendered in a trace.
- Try it live in **LangGraph Studio** (`langgraph dev`).
- Tracing **non-LangChain** frameworks: **Strands** (one-line prebuilt integration, with a tool +
  subagent), **OpenTelemetry** (point the OTLP endpoint at LangSmith / replay raw spans), and
  **`@traceable`** (hand-rolled agents) — all routed to a separate `-integrations` project.
- Finishes by seeding a larger batch of traces, including deliberate hallucination / PII failures.

### `02_online_evals.ipynb` — Online Evaluations
- Set up evaluators in LangSmith that score **live traces** automatically.
- **Thread-level task completion** (LangChain Tuned), **PII** and **completeness** (fast Decision Model
  judges), **toxicity** (LLM judge, **aligned** to human labels), **hallucination** (LLM judge).
- A **composite** overall-quality score, **trace-level conditional filters** (e.g. conciseness only after
  no hallucination), and **cost controls** (sampling, model choice, filters).
- Seeds traces at the end so the evaluators score them.

### `03_offline_evals.ipynb` — Offline Evaluations
- Build (or curate via annotation queue) a **dataset**, then run experiments at three granularities:
  **final-response (e2e)**, **single-step** (first tool), and **trajectory** (tool sequence).
- **A/B test prompt versions** pulled from **Context Hub**, each run as its own experiment with metadata.
- Per-user datasets so everyone views their own results.

### `04_finding_failure_modes.ipynb` — Finding Failure Modes
- **Engine** — closed-loop failure detection, root-cause diagnosis, fix PRs, suggested evaluators, and
  generated dataset examples; plus **red teaming** (adversarial probes) and **fix verification** against a
  deployment (baseline vs after-PR). Runs on cloud **and self-hosted**, with managed or your-own model.
- **Chat** — ask natural-language questions grounded in your traces/experiments.
- **Insights Agent** — automated pattern discovery across the trace corpus.

### `05_annotation_queues.ipynb` — Annotation Queues
- Route low-scoring runs (e.g. `hallucination = 1`) to a **human-review queue** via a run rule.
- Create queues (UI + SDK), review/label in the UI, and feed the labeled runs back into Module 3 datasets.

---

## Tests

```bash
uv run --extra dev pytest -q
```

Covers the pure-logic utilities (config/project naming, mock data, tools, seeding).
