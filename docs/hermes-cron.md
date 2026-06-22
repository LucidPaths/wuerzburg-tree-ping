# Hermes cron setup

This repo is intentionally a set of plain Python monitors. Hermes can wrap any folder as a scheduled watchdog.

## Script-only watchdog

Use this shape when you want zero LLM cost on normal ticks:

- Schedule: `every 1h`
- Script: `cd /path/to/OpenDataWuerzburg-Possibilities && python usecases/<folder>/<script>.py`
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
Run the selected Würzburg OpenData script. If the script outputs data, rewrite it as a concise human-readable Telegram ping with: location, measured values, likely meaning, and suggested next action. Preserve timestamps. Do not invent data.
```

Script examples:

```bash
cd /path/to/OpenDataWuerzburg-Possibilities && python usecases/tree-watering-ping/tree_watering_ping.py
cd /path/to/OpenDataWuerzburg-Possibilities && python usecases/parking-ping/parking_ping.py
cd /path/to/OpenDataWuerzburg-Possibilities && python usecases/bike-counter-pulse/bike_counter_pulse.py
```

This preserves the boundary: the script emits measured facts; Hermes explains them.
