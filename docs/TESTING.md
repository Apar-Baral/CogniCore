# Testing CogniCore Features

Checklist to verify install and all feature clusters on **Windows**, **Linux**, or **Kali (VMware)**.

Use a throwaway folder: `~/projects/cognition-test`.

---

## Smoke test (5 min)

```bash
export PATH="$HOME/.hermes/hermes-agent/venv/bin:$PATH"
hermes-cognition doctor
hermes plugins list | grep cognition
python3 -c "import yaml; yaml.safe_load(open('$HOME/.hermes/config.yaml')); print('config OK')"
hermes tools list | head -30
```

| Check | Pass |
|-------|------|
| doctor → OK cognition-engine | ☐ |
| cognition enabled in plugins list | ☐ |
| config.yaml parses | ☐ |
| `write_file` in tools list | ☐ |

---

## CLI tests

```bash
cd ~/projects/cognition-test && mkdir -p ~/projects/cognition-test && cd $_
git init
hermes-cognition init
hermes-cognition plan "Tiny Python CLI with 2 files"
hermes-cognition status --detailed
hermes-cognition graphify index
hermes-cognition graphify navigate "add main entrypoint"
hermes-cognition graphify status
```

| Test | Pass |
|------|------|
| `.cognition/dna.json` exists | ☐ |
| plan adds phases | ☐ |
| `graphify.json` exists | ☐ |

---

## Hermes session tests

```bash
hermes-cognition start "test"
hermes -t terminal,file,web -z "Call cognition_status detailed true and reply OK"
hermes-cognition end
```

| Test | Pass |
|------|------|
| Bootstrap / mission context on first turn | ☐ |
| `cognition_status` works in chat | ☐ |

**Shield:** In Hermes, ask to write a file importing `nonexistent_pkg_xyz_999`. Expect block or warning.

**Budget:** `cognition_budget` in chat; optional low `session_tokens` in config.

**Delegate:** `cognition_delegate` role `backend` with toolsets `["terminal","file"]`.

---

## Transfer

```bash
hermes-cognition register-project
ls ~/.cognition/projects/
hermes-cognition suggest-plan "Another CLI project"
```

---

## Do not use

```bash
hermes -t cognition   # WRONG for building code — no file/terminal tools
```

Use `hermes` or `hermes -t terminal,file,web`.

---

## Full matrix

```
☐ Install: doctor, plugins, config
☐ CLI: init, plan, status, graphify index/navigate/status
☐ Hooks: bootstrap, shield, budget (observed in session)
☐ Tools: status, phase_update, validate, budget, graphify_*
☐ Transfer: register-project, suggest-plan
☐ Agent build: hermes + file + terminal toolsets
```

See [USER_GUIDE.md](USER_GUIDE.md) for details per feature number.
