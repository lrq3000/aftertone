---
name: aftertone-doctor
description: Diagnose Aftertone hooks, config, and daemon
---

Run **only** this from the **Aftertone install root**:

```
uv run --directory py python -m aftertone doctor
```

Summarize `checks_ok` and `issues` from the JSON. No other edits.
