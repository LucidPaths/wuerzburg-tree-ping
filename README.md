# OpenData Würzburg Possibilities

TL;DR: an assortment of small, simple Würzburg OpenData solutions — each folder is a self-contained demo with a Python script, Telegram staging, Hermes cron/agent notes, and a path to visualization.

Clean boundary: **Python does truth; Hermes does scheduling, interpretation, and delivery.**

Verified portal: <https://opendata.wuerzburg.de/>

API base:

```text
https://opendata.wuerzburg.de/api/explore/v2.1/catalog/datasets
```

## Usecases

| Folder | Demo | Dataset(s) |
| --- | --- | --- |
| [`usecases/tree-watering-ping`](usecases/tree-watering-ping) | Tree/garden soil moisture and water storage alert. | `sls-klimabaeume`, `tektelic-kiwi-agriculture-sensor_klimagarten-ochsenfurt`, `milesight-em500_klimagarten-ochsenfurt` |
| [`usecases/parking-ping`](usecases/parking-ping) | Parking garage status and alternatives. | `parkplatzdaten_wuerzburg` |
| [`usecases/bike-counter-pulse`](usecases/bike-counter-pulse) | Busiest bike counter stations. | `fahrradzaehlung-tagesdaten-alle-zaehlstationen` |
| [`usecases/pedestrian-downtown-pulse`](usecases/pedestrian-downtown-pulse) | Downtown pedestrian activity pulse. | `passantenzaehlung_tagesdaten` |
| [`usecases/waste-pickup-reminder`](usecases/waste-pickup-reminder) | Waste pickup reminders by district. | `abfallkalender-wuerzburg` |
| [`usecases/accessible-toilets-helper`](usecases/accessible-toilets-helper) | Nearest accessible toilets from a location. | `barrierefreie-toiletten-im-stadtgebiet-wuerzburg` |
| [`usecases/zdi-event-digest`](usecases/zdi-event-digest) | ZDI/startup event digest. | `eventfeed` |

## Quick start

```bash
git clone https://github.com/LucidPaths/OpenDataWuerzburg-Possibilities.git
cd OpenDataWuerzburg-Possibilities
python -m venv .venv
. .venv/bin/activate  # Windows git-bash / Linux / macOS
pip install -e .
```

Run scripts directly:

```bash
python usecases/tree-watering-ping/tree_watering_ping.py
python usecases/parking-ping/parking_ping.py
python usecases/bike-counter-pulse/bike_counter_pulse.py
python usecases/pedestrian-downtown-pulse/pedestrian_downtown_pulse.py
python usecases/waste-pickup-reminder/waste_pickup_reminder.py --district Grombühl
python usecases/accessible-toilets-helper/accessible_toilets_helper.py --lat 49.7939 --lon 9.9300
python usecases/zdi-event-digest/zdi_event_digest.py
```

Or use installed commands:

```bash
wuerzburg-tree-ping
wuerzburg-parking-ping
wuerzburg-bike-ping
wuerzburg-pedestrian-ping
wuerzburg-waste-ping --district Grombühl
wuerzburg-toilets-ping --lat 49.7939 --lon 9.9300
wuerzburg-events-ping
```

## Telegram staging

Telegram support is staged for every usecase. Set credentials when you have a bot/chat target:

```bash
export TELEGRAM_BOT_TOKEN="<bot-token>"
export TELEGRAM_CHAT_ID="<chat-id>"
python usecases/parking-ping/parking_ping.py --send-telegram
```

Secrets stay in environment variables. Do **not** commit them.

## Hermes cron / agent setup

Every usecase folder has a `HERMES.md` with a script-only cron shape and an LLM-enhanced prompt.

Reliable watchdog pattern:

```bash
cd /path/to/OpenDataWuerzburg-Possibilities && python usecases/parking-ping/parking_ping.py
```

Inside Hermes, create cron jobs with `no_agent=True` for pure delivery:

- stdout = Telegram/Discord message
- empty stdout = silent, for alert-style scripts
- non-zero exit = error alert

For an “AI demo” mode, keep the script as source of truth and ask Hermes to rewrite/explain the measured output. Do not let the model invent data.

## Dashboard / visualizer

Generate a dependency-free static dashboard snapshot:

```bash
python dashboard/generate_dashboard.py
```

Open:

```text
dashboard/index.html
```

## Event framing

1. Show the public OpenData source.
2. Show the dataset ID and live JSON fields.
3. Run one local script.
4. Show Telegram/Hermes delivery.
5. Ask Hermes: “why did this trigger?” or “what should I do next?”

This keeps the demo grounded: AI explains and prioritizes, but municipal data decides.

## Development

```bash
python -m pytest
python dashboard/generate_dashboard.py
```
