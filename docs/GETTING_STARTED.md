# Getting started (5 minutes)

Read this first if you are new.  
**What we build:** [VISION.md](VISION.md) · **All features:** [USER_GUIDE.md](USER_GUIDE.md)

---

## What you need

1. [Hermes Agent](https://github.com/NousResearch/hermes-agent) installed  
2. This repo cloned  
3. A **project folder of your own** (not only the CogniCore repo)

---

## Install

```bash
git clone https://github.com/Apar-Baral/CogniCore.git
cd CogniCore
bash scripts/install-hermes-cognition.sh
export PATH="$HOME/.hermes/hermes-agent/venv/bin:$PATH"
hermes-cognition doctor
```

Expect: `active engine: cognicore-bundled`

---

## Use on YOUR project (important)

```bash
cd /path/to/your-app          # e.g. ~/projects/my-app
hermes-cognition init
hermes-cognition plan "Describe what you want to build in one sentence"
hermes-cognition status --detailed
```

You should see **your phases** in the terminal — not a fixed “Phase 01 XSS” unless your goal says so.

---

## See your plan

```bash
hermes-cognition status              # short
hermes-cognition status --detailed   # full phase list  ← use this
cat .cognition/dna.json            # raw data
```

---

## See Graphify (file map)

```bash
hermes-cognition graphify index
hermes-cognition graphify status
hermes-cognition graphify navigate "implement the main feature"
cat .cognition/graphify.json
```

---

## Build code with Hermes

```bash
hermes -t terminal,file,web
```

In chat, say what to build. CogniCore runs in the background (bootstrap, shield, budget).

**Do not use** `hermes -t cognition` only — that disables file/terminal tools.

---

## Daily loop

```text
init once → plan (your goal) → graphify index (optional)
→ hermes (build) → status (check progress) → end (end of day)
```

---

## Example project (optional)

We ship an **example** XSS scanner, not the main product:

```bash
cd examples/xss-finder
pip install -e .
# See examples/xss-finder/README.md
```

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `initialized False` in CogniCore repo | Run `init` in **your** project folder |
| Plan seems “wrong” | Run `plan` again with a clearer goal |
| Hermes cannot write files | Use `hermes -t terminal,file,web` |
| Truncated responses | One file per Hermes message — [HERMES_TIPS.md](HERMES_TIPS.md) |

---

## Next docs

| Doc | When |
|-----|------|
| [PLUGIN.md](PLUGIN.md) | Understand tools and hooks |
| [FEATURE_MAP.md](FEATURE_MAP.md) | All 54 features |
| [TESTING.md](TESTING.md) | Verify install |
