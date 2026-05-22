# Avoid Hermes "Response truncated" when building code

If Hermes stops with:

```text
Error: Response remained truncated after 3 continuation attempts
```

the model hit **max output tokens** while trying to write a large file in one tool call.

## Fixes

### 1. One file per message

```text
Create only xss_finder/config.py for Phase 01 scope and safety. Stop after one file.
```

Then next message:

```text
Create xss_finder/scope.py only. Stop.
```

### 2. Use full toolsets

```bash
hermes -t terminal,file,web
```

Not:

```bash
hermes -t cognition
```

### 3. Copy from CogniCore examples

Phase 01 reference is already in the repo:

```bash
cp -r ~/Desktop/CogniCore/examples/xss-finder/xss_finder ~/projects/xss-finder/
```

### 4. Smaller model temperature / shorter goals

Break phases into single-file tasks in `hermes-cognition plan`.

### 5. Use CLI yourself

```bash
cd examples/xss-finder
pip install -e .
xss-finder scan URL --i-agree --allow-host HOST
```

Hermes + CogniCore orchestrate; you can implement files manually when the model truncates.
