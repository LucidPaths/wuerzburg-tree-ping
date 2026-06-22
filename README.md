# Würzburg OpenData Pings

Small demo scripts that turn Würzburg OpenData into useful Telegram/Hermes pings.

Clean boundary: **Python does truth; Hermes does scheduling, interpretation, and delivery.**

Verified portal: <https://opendata.wuerzburg.de/>

API base:

```text
https://opendata.wuerzburg.de/api/explore/v2.1/catalog/datasets
```

## Usecases

| Folder | Demo | Datasets |
| --- | --- | --- |
| [`usecases/tree-watering-ping`](usecases/tree-watering-ping) | Watches tree/garden soil moisture and water storage; pings when watering review is needed. | `sls-klimabaeume`, `tektelic-kiwi-agriculture-sensor_klimagarten-ochsenfurt`, `milesight-em500_klimagarten-ochsenfurt` |
| [`usecases/parking-ping`](usecases/parking-ping) | Watches parking facility status; pings occupied garages and likely alternatives. | `parkplatzdaten_wuerzburg` |

## Quick start

```bash
git clone https://github.com/LucidPaths/wuerzburg-tree-ping.git
cd wuerzburg-tree-ping
python -m venv .venv
. .venv/bin/activate  # Windows git-bash / Linux / macOS
pip install -e .
```

Run the two demos:

```bash
wuerzburg-tree-ping
wuerzburg-parking-ping
```

Or run by folder:

```bash
python usecases/tree-watering-ping/tree_watering_ping.py
python usecases/parking-ping/parking_ping.py
```

JSON/debug mode:

```bash
wuerzburg-tree-ping --json
wuerzburg-parking-ping --json
```

## Telegram direct mode

Create a Telegram bot with BotFather, get the chat ID, then:

```bash
export TELEGRAM_BOT_TOKEN="<bot-token>"
export TELEGRAM_CHAT_ID="<chat-id>"
wuerzburg-tree-ping --send-telegram
wuerzburg-parking-ping --send-telegram
```

Secrets stay in environment variables. Do **not** commit them.

## Hermes cron mode

Recommended for a local Hermes demo because Hermes already has gateway delivery.

Script-only watchdog shape:

```bash
cd /path/to/wuerzburg-tree-ping && python usecases/tree-watering-ping/tree_watering_ping.py
cd /path/to/wuerzburg-tree-ping && python usecases/parking-ping/parking_ping.py
```

If creating from inside Hermes with the `cronjob` tool, use `no_agent=True` for a pure watchdog:

- empty stdout = silent
- non-empty stdout = delivered
- non-zero exit = error alert

LLM-enhanced mode is also viable: let the script emit measured facts, then ask Hermes to rewrite them as a concise human ping.

More detail: [`docs/hermes-cron.md`](docs/hermes-cron.md)

## Other easy OpenData demo candidates found

I checked the portal catalog and these are good next-usecase candidates:

| Dataset | Why it is easy |
| --- | --- |
| `fahrradzaehlung-tagesdaten-alle-zaehlstationen` | Daily bike counts by station; easy “which route is busiest?” ping. |
| `passantenzaehlung_tagesdaten` / `passantenzaehlung_stundendaten` | Pedestrian counts for city-center locations; easy downtown activity pulse. |
| `abfallkalender-wuerzburg` | Waste pickup dates by district; easy reminder bot, but needs district selection. |
| `barrierefreie-toiletten-im-stadtgebiet-wuerzburg` | Accessibility/location helper; easy “nearest public toilet” style demo if user location is supplied. |
| `eventfeed` | ZDI event feed; easy “upcoming startup/tech events” digest. |
| `fahrradstellplaetze-stadt-wuerzburg` | Bike parking / e-bike charging / carsharing locations; easy map/search helper. |

Best next demo after parking: **bike counter pulse**. It has simple numeric data and a natural AI explanation layer: “where is cycling traffic highest today?”

## Example pings

```text
🌳 Würzburg OpenData watering ping (2026-06-22 09:30 UTC)

🔴 Dry soil: Ahorn
Soil moisture at 30 cm is 3.5%, 100 cm: 3.8%, air temp: 29.3°C. Recommend watering review.
```

```text
🅿️ Würzburg parking ping (2026-06-22 11:52 UTC)
Avoid / check before driving:
- Würzburg Juliusspital: belegt
Likely available options:
- Würzburg Marktgarage: frei
- Würzburg PH Mitte: frei
```

## Development

```bash
python -m pytest
python -m wuerzburg_tree_ping.cli --json
python -m wuerzburg_tree_ping.parking --json
```

## Notes for the event

Good demo script:

1. Show the public OpenData source.
2. Show the dataset IDs and live JSON fields.
3. Run a local monitor.
4. Show the Telegram/Hermes ping.
5. Ask Hermes: “why did this trigger?” or “what should I do next?”

This keeps the demo grounded: AI explains and prioritizes, but municipal data decides.
