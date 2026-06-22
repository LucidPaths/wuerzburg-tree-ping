from __future__ import annotations

from pathlib import Path
import html
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wuerzburg_tree_ping import bike, cli, events, parking, pedestrian, toilets, waste

USECASES = [
    ("Tree watering", "tree-watering-ping", cli.render_alerts(cli.build_alerts())),
    ("Parking", "parking-ping", parking.build_ping()),
    ("Bike counter", "bike-counter-pulse", bike.build_ping()),
    ("Pedestrian pulse", "pedestrian-downtown-pulse", pedestrian.build_ping()),
    ("Waste pickup", "waste-pickup-reminder", waste.build_ping()),
    ("Accessible toilets", "accessible-toilets-helper", toilets.build_ping()),
    ("ZDI events", "zdi-event-digest", events.build_ping()),
]


def card(title: str, folder: str, text: str) -> str:
    body = html.escape(text or "No current alert/output.")
    return f"""
    <section class="card">
      <h2>{html.escape(title)}</h2>
      <p><code>usecases/{html.escape(folder)}</code></p>
      <pre>{body}</pre>
    </section>
    """


def build_html() -> str:
    cards = "\n".join(card(*entry) for entry in USECASES)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>OpenData Würzburg Possibilities</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 0; background: #101418; color: #eef3f8; }}
    header {{ padding: 32px; background: linear-gradient(135deg, #0f766e, #1d4ed8); }}
    main {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; padding: 16px; }}
    .card {{ background: #18212b; border: 1px solid #2c3a47; border-radius: 16px; padding: 18px; box-shadow: 0 8px 24px #0005; }}
    h1 {{ margin: 0 0 8px; }}
    h2 {{ margin-top: 0; }}
    code {{ color: #93c5fd; }}
    pre {{ white-space: pre-wrap; background: #0b1117; border-radius: 12px; padding: 12px; overflow: auto; }}
  </style>
</head>
<body>
  <header>
    <h1>OpenData Würzburg Possibilities</h1>
    <p>Assortment of small simple OpenData demos: scripts, Telegram staging, Hermes cron, and visual pings.</p>
  </header>
  <main>{cards}</main>
</body>
</html>"""


def main() -> int:
    out = Path(__file__).with_name("index.html")
    out.write_text(build_html(), encoding="utf-8")
    print(out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
