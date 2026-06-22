from __future__ import annotations
import json, sys
from .common import PingItem, fetch_records, render_ping, send_telegram
DATASET_ID='passantenzaehlung_tagesdaten'

def latest_top(records, top_n=5):
    if not records: return []
    latest=max(str(r.get('timestamp','')) for r in records)
    same=[r for r in records if str(r.get('timestamp',''))==latest]
    same.sort(key=lambda r: r.get('pedestrians_count') or 0, reverse=True)
    return same[:top_n]

def build_items(records=None):
    records = records if records is not None else fetch_records(DATASET_ID, limit=80, order_by='timestamp desc')
    return [PingItem(str(r.get('location_name','unknown location')), f"{int(r.get('pedestrians_count') or 0):,} pedestrians; weather {r.get('weather_condition','unknown')}, temp {r.get('temperature','?')}°C.", r.get('timestamp')) for r in latest_top(records)]

def build_ping(): return render_ping('🚶','Würzburg downtown activity pulse', build_items())
def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv); items=build_items()
    if '--json' in argv: print(json.dumps([i.__dict__ for i in items], ensure_ascii=False, indent=2)); return 0
    text=render_ping('🚶','Würzburg downtown activity pulse',items)
    if '--send-telegram' in argv: send_telegram(text)
    else: print(text)
    return 0
if __name__=='__main__': raise SystemExit(main())
