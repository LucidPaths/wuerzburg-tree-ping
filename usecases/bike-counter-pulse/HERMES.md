# Hermes setup — 🚲 Bike counter pulse

## Script-only cron

Use `no_agent=True` for reliable scheduled delivery:

```bash
cd /path/to/OpenDataWuerzburg-Possibilities && python usecases/bike-counter-pulse/bike_counter_pulse.py
```

Delivery semantics:

- stdout is the Telegram/Discord message
- non-zero exit becomes an error alert
- tokens stay in environment variables if direct Telegram mode is used

## LLM-enhanced prompt

```text
Run the 🚲 Bike counter pulse OpenData script. Preserve measured facts and timestamps. Rewrite the output as a concise human-readable ping with the likely meaning and a suggested next action. Do not invent data beyond stdout.
```
