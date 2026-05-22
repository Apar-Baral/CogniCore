---
name: cognition-dev-orchestrator
description: Use Cognition Engine tools for phased development, shield validation, and session continuity.
---

# Cognition development orchestrator

When working in a repo with `.cognition/dna.json` or `.hermes/cognition/dna.json`:

1. Run `cognition_init` once per project if DNA is missing.
2. Run `cognition_plan` with the user's goal before large builds.
3. At session start, read injected `<cognition_bootstrap>` context — follow CURRENT MISSION and DO NOT REPEAT.
4. Before writing files, prefer `cognition_validate` on non-trivial code.
5. Use `cognition_status` to see phase progress; `cognition_phase_update` when completing work.
6. Use `cognition_delegate` with roles (architect, backend, frontend, security, test, docs, refactor) for parallel work.
7. Use `cognition_budget` when the user asks about token spend.
8. On scope changes, use `cognition_impact` before adding features.

## Graphify (token-optimized navigation)

- Run `cognition_graphify_index` after refactors or when the graph is stale.
- Before broad `read_file` / search, call `cognition_graphify_navigate` with your task and respect the returned file plan.
- Each turn, `<graphify_navigation>` in context lists priority files — read those first.
- Use `cognition_graphify_status` to see over-read files; avoid re-reading paths listed under skip_rereads.

Hermes slash: `/cognition status`, `/cognition plan <goal>`, `/cognition end`.

CLI: `hermes cognition graphify index|navigate <task>|status`
