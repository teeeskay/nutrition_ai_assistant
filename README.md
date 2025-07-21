# 🧠 Nutrition & Wellness Planner (Agentic AI Stack)

This is a modular, agent-based wellness planner app built using LangGraph, open-source LLMs (e.g., Mistral, BioGPT), and local datasets. It guides users through understanding their nutritional needs, refining their diet, selecting recipes, and generating grocery lists—all through a natural, conversational interface with user-in-the-loop control.

---

## 📦 Key Features

- Multi-step conversational assistant
- Modular AI agent workflows (RDI, Gap Analysis, Recipe, Grocery, etc.)
- Dynamic user feedback, edit, and reroute support
- Supports implicit confirmation and adaptive flow progression
- Synthetic and local datasets (RDI, food nutrients, prices)

---

## 🚀 Tech Stack

| Layer       | Tools |
|-------------|-------|
| Agent Logic | LangGraph, Python |
| LLMs        | Mistral / BioGPT / Together.ai |
| UI          | Streamlit |
| Data        | Local CSV/JSON |
| Testing     | Pytest |
| Versioning  | Git + GitHub |

---

## 🛠️ Getting Started (with Cursor)

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd nutrition_ai_architecture_export
```

### 2. Open in [Cursor](https://www.cursor.so/)
- Launch Cursor
- Open the cloned folder
- Use the built-in terminal to install requirements

```bash
pip install -r requirements.txt
```

### 3. Launch Streamlit App (when built)
```bash
streamlit run ui/streamlit_app.py
```

---

## 🧪 Recommended Build & Test Flow (Senior/Lead Engineering Style)

### 🔁 Iterative Build-Validate Loop

1. **Define Schema** first — start with `schemas.py`
2. **Build 1 Agent at a Time** (e.g., `rdi_agent`)
3. **Write Pytest Unit Tests** per agent (e.g., `test/test_rdi_agent.py`)
4. **Build LangGraph flow** only once agents are working individually
5. **Use Streamlit or CLI for testing** agent outputs
6. **Mock LLM calls where needed** for faster feedback loops
7. **Keep commits small & tested**, follow feature branches → PR → Merge

---

## 🧱 Suggested First Milestone (MVP 1.0)

1. ✅ `schemas.py` (already done)
2. 🧠 `rdi_agent.py` — calculate nutritional needs from UserProfile
3. 🧪 `test_rdi_agent.py` — test RDI output structure
4. 🔁 `langgraph/planner.graph.yaml` with RDI + mock downstream
5. 🖥️ `streamlit_app.py` — basic input/output flow

Once working, proceed to:
- `intake_agent` + `gap_agent`
- Add `recipe_agent`, `feedback_agent`, and `grocery_agent`
- Connect `session_store.py` for week tracking

---

## 📁 File Structure (Overview)

- `agents/` — each agent module (rdi_agent, recipe_agent, etc.)
- `core/` — prompts, search wrappers, BioGPT interface
- `shared/` — schemas and constants
- `ui/` — Streamlit interface (editable panels)
- `langgraph/` — planner.graph.yaml for orchestration
- `data/` — local datasets
- `test/` — unit tests

---

## 🧩 To Do Next (Scaffold Suggestion)

- [ ] `agents/rdi_agent.py`
- [ ] `test/test_rdi_agent.py`
- [ ] `core/session_store.py`
- [ ] `core/router_agent.py`
- [ ] `ui/streamlit_app.py`

Happy building 🚀
