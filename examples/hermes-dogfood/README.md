# Hermes Cognition dogfood

Minimal project to verify the plugin.

```bash
cd examples/hermes-dogfood
hermes cognition init
hermes cognition plan "Demo app with CLI and tests"
hermes cognition status --detailed
```

Expected: `.cognition/dna.json` created and phase map printed.
