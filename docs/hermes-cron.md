# Hermes cron setup

This repo is intentionally a plain Python monitor. Hermes can wrap it as a scheduled watchdog.

## Script-only watchdog

Use this shape when you want zero LLM cost on normal ticks:

- Schedule: `every 1h`
- Script: `cd /path/to/wuerzburg-tree-ping && python -m wuerzburg_tree_ping.cli`
- `no_agent=True`
- Deliver: `telegram`, `discord`, or `origin`

Behavior:

- Empty stdout: no message sent.
- Non-empty stdout: alert delivered verbatim.
- Non-zero exit: Hermes sends an error alert.

## LLM-enhanced cron

Use this when the demo wants Hermes to explain/prioritize the result:

Prompt:

```text
Run the Würzburg OpenData watering monitor. If the script outputs alerts, rewrite them as a concise human-readable Telegram ping with: location, measured values, likely issue, and suggested next action. If stdout is empty, say nothing.
```

Script:

```bash
cd /path/to/wuerzburg-tree-ping && python -m wuerzburg_tree_ping.cli
```

This preserves the boundary: the script emits measured facts; Hermes explains them.
