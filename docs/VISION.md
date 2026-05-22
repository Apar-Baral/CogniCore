# What we are building (CogniCore)

## One sentence

**CogniCore is a Hermes Agent plugin that gives AI coding sessions a real project brain** — memory, plans, safety checks, budget control, and smart file navigation — so Hermes can build software in your repo without forgetting context every time you restart.

---

## The problem we solve

| Without CogniCore | With CogniCore |
|-------------------|----------------|
| Hermes forgets what phase you were on | Phases and goals live in `.cognition/dna.json` |
| Same import mistakes repeat | Shield can block bad writes |
| Token spend runs away | Budget zones + wrap-up at 90% |
| Agent re-reads the whole repo | Graphify suggests relevant files only |
| You re-explain the project every session | Bootstrap injects mission + “do not repeat” |

---

## What CogniCore is

- A **Hermes plugin** (`hermes-cognition`) you install into the Hermes Python venv  
- A **self-contained** package — no second repo required to run  
- A **per-project** `.cognition/` folder (DNA, plan, graph, sessions)  
- A **spec of 54 features** ([Features.txt](../Features.txt)) implemented as 14 tools + 8 hooks + Graphify  

---

## What CogniCore is NOT

| Misconception | Truth |
|---------------|--------|
| “It auto-builds my whole app alone” | **Hermes** writes code. CogniCore **plans, remembers, and protects**. |
| “Phase 1 is hardcoded for everyone” | Phases come from **your goal** via `hermes-cognition plan "..."`. Change the goal → new plan. |
| “Same as CognitionEngine repo” | [CognitionEngine](https://github.com/Apar-Baral/CognitionEngine) is a **separate** research/library project. CogniCore does not require it. |
| “Only for XSS scanner” | `examples/xss-finder/` is **one sample**. Use CogniCore on any codebase. |

---

## How planning works (not hardcoded)

```text
You type a goal:
  hermes-cognition plan "Build a CLI tool with auth and tests"

CogniCore writes phases into:
  your-project/.cognition/dna.json

You see the plan:
  hermes-cognition status --detailed

Hermes implements it:
  hermes -t terminal,file,web
```

Phases are **generated from your goal text**, not copied from a fixed XSS template.  
The bundled planner uses sensible default phase names (scaffold, core logic, tests, docs, security review, …) and ties them to your goal.

To **change** the plan: run `plan` again with a new goal, or let Hermes call `cognition_plan` / `cognition_phase_update` in chat.

---

## Who this is for

- Developers using **Hermes Agent** on real repos  
- Teams that want **session continuity** and **token discipline**  
- Security / app builders who want **guardrails** (shield, scope in examples)  
- Anyone implementing the 54-feature Cognition spec on top of Hermes  

---

## Repository layout (what each part is for)

| Path | Purpose |
|------|---------|
| `packages/hermes-cognition/` | The plugin Hermes loads |
| `packages/hermes-cognition/hermes_cognition/bundled/` | Built-in engine (DNA, plan, shield, budget) |
| `packages/hermes-cognition/hermes_cognition/graphify/` | Project graph + navigation |
| `config/cognition.example.yaml` | Hermes config snippet |
| `scripts/install-hermes-cognition.*` | Install into Hermes venv |
| `examples/xss-finder/` | **Example app** (authorized XSS CLI) — not the core product |
| `examples/hermes-dogfood/` | Minimal config sample |
| `Features.txt` | Full 54-feature specification |
| `docs/` | Guides for humans |

---

## Success criteria (what “done” looks like for users)

1. Install CogniCore in Hermes venv in under 5 minutes  
2. Run `init` + `plan` in **their** project directory  
3. See a clear phased roadmap with `status --detailed`  
4. Run `hermes -t terminal,file,web` and get bootstrap + shield + graphify in the loop  
5. Resume tomorrow without re-explaining the project  

---

## Roadmap (project direction)

| Now | Next |
|-----|------|
| Self-contained bundled engine | Richer planning heuristics |
| 14 tools + 8 hooks + Graphify | Deeper shield / semantic index (optional) |
| Example xss-finder | More examples (API, CLI, library) |
| Docs + install scripts | PyPI publish `hermes-cognition` |

Contributions should align with: **Hermes plugin first**, **per-project `.cognition/`**, **goal-driven plans**, **no mandatory external engine repo**.
