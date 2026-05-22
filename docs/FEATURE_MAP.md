# CogniCore feature map (54 capabilities)

CogniCore implements these as **14 Hermes tools**, **8 hooks**, **Graphify**, and the **`hermes-cognition` CLI**.  
Full spec: [Features.txt](../Features.txt).

| Cluster | IDs | What you get | How to use |
|---------|-----|--------------|------------|
| **A — Memory** | 1–6, 19–23, 28 | DNA, phases, avoid registry, bootstrap | `init`, `plan`, `status`, hooks |
| **B — Shield** | 7–12 | Import/code validation before writes | `cognition_validate`, `pre_tool_call` |
| **C — Budget** | 13–18 | GREEN→YELLOW→RED→wrap-up | `cognition_budget`, hooks |
| **D — Planning** | 24–28 | Phase plans, impact hints | `plan`, `cognition_impact` |
| **E — Visualization** | 29–34 | Progress maps in status | `status --detailed` |
| **F — Learning** | 35–41 | Session end persistence | `end`, `on_session_end` |
| **G — Transfer** | 42–45 | Cross-project registry | `register-project`, `suggest-plan` |
| **H — Multi-agent** | 46–49 | Role-based delegate | `cognition_delegate` |
| **I — Models** | 50–54 | Model tier hints | `cognition_recommend_model` |
| **Graphify** | — | File graph + navigation | `graphify index/navigate` |

Architecture diagram: [cognicore-architecture.svg](assets/cognicore-architecture.svg)
