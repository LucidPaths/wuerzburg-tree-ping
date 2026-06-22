# Dashboard / visualizer

A dependency-free localhost dashboard for the Würzburg OpenData demos.

It gives the demo one visual surface instead of seven terminal windows:

- tree watering sensor alerts
- parking status
- bike counter pulse
- pedestrian downtown pulse
- waste pickup reminders
- nearby accessible toilets
- ZDI/event digest

## Run live dashboard

From repo root:

```bash
python dashboard/app.py
```

Open:

```text
http://127.0.0.1:8765/
```

The browser calls:

```text
/api/snapshot
```

That reruns the local Python collectors against `opendata.wuerzburg.de` and redraws the cards.

Optional controls:

- `district` filters the waste calendar, e.g. `Grombühl`
- `lat` / `lon` changes the accessible-toilet search point

## Generate static fallback

For offline-ish demos or screenshots:

```bash
python dashboard/generate_dashboard.py
```

Open:

```text
dashboard/index.html
```

The static HTML embeds the last collected snapshot. The live localhost mode is better for the actual presentation.
