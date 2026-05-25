# CogniCore troubleshooting

## Hermes stops or gives up after ~1 minute

Usually caused by **aggressive plugin settings** in `~/.hermes/config.yaml` (from an older install).

### Fix (recommended)

Edit `~/.hermes/config.yaml` (or `%LOCALAPPDATA%\hermes\config.yaml` on Windows):

```yaml
cognition:
  shield:
    mode: syntax
    block_writes: false
  budget:
    enabled: true
    zones: false
    enforce_tool_blocks: false
    wrap_up_messages: false
    session_tokens: 500000
  graphify:
    inject_on_llm: false
    auto_index: false
```

Then reinstall the plugin and restart Hermes:

```bash
cd CogniCore
git pull
bash scripts/install-hermes-cognition.sh   # or .ps1 on Windows
hermes-cognition doctor
```

### What was going wrong

| Setting | Effect |
|---------|--------|
| `shield.block_writes: true` + strict import checks | Blocks `write_file` / `patch` when imports cannot be resolved |
| `budget.zones: true` | Injects “wrap up at 90%” every turn; model stops coding early |
| `budget.enforce_tool_blocks` (implicit via exhausted budget) | Disables terminal and file tools at 100% |
| Stale `tokens_used` in `.cognition/session_state.json` | Budget looks exhausted immediately |
| `graphify.inject_on_llm: true` | Huge extra context every turn → slow / costly |
| `graphify.auto_index: true` | Full repo scan on every Hermes session start |

### Clear a stuck budget counter

In your **project** directory (where `.cognition/` lives):

```bash
# optional: end cognition session cleanly
hermes-cognition end
# or reset token meter in session state
python3 -c "
import json
from pathlib import Path
p = Path('.cognition/session_state.json')
if p.is_file():
    d = json.loads(p.read_text())
    d['tokens_used'] = 0
    p.write_text(json.dumps(d, indent=2))
    print('reset tokens_used')
"
```

### Hermes must have file + terminal tools

```bash
hermes -t terminal,file,web
```

Not only `hermes -t cognition` — that cannot write code.
