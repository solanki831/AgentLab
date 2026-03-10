# AgentLab — Day-to-Day Testing Workbench

Chain-first agent workbench for day-to-day API testing, LLM evaluation, and
multi-agent orchestration — with built-in **context chunking** so large
responses are split automatically before being passed to the next agent in a
chain.

Quick start

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run framework/agentlab.py --server.port 8503
```

Linux / macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run framework/agentlab.py --server.port 8503
```

Project layout

- `framework/agentlab.py` — main Streamlit entrypoint (**AgentLab**)
- `framework/` — framework modules (agents, registry, helpers)
- `scripts/` — convenience scripts to run and setup environment
- `docs/` — documentation index (links to existing MD files)

Key features

- **Chain Builder** tab — wire agents sequentially; output of each step
  becomes the context input of the next
- **Context Chunking** — large API/LLM outputs are automatically split into
  overlapping chunks (size & overlap configurable in the sidebar)
- **Agent Catalog** — browse and run any registered agent
- **Test Lab** — interactive single-agent tester with full auth/API config
- **Natural Language Tests** — describe a test in plain English
- **LLM Playground** — benchmark Ollama models
- **Orchestration** — run parallel multi-agent suites

Notes

- Ollama is expected to run locally for LLM tests (see OLLAMA_GUIDE.md)
- Use `verify_agents.py` to run quick verification checks

If you want me to also move documentation files into `docs/` or create a package layout (`src/`), tell me and I'll do it.