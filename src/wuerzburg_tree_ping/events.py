from __future__ import annotations
from datetime import datetime, timezone
import json, sys
from .common import PingItem, fetch_records, render_ping, send_telegram
DATASET_ID='eventfeed'

def upcoming(records, limit=8):
    now=datetime.now(timezone.utc).isoformat()
    rows=[r for r in records if str(r.get('pubdate','')) >= now]
    rows.sort(key=lambda r: str(r.get('pubdate','')))
    return rows[:limit]

def build_items(records=None):
    records = records if records is not None else fetch_records(DATASET_ID, limit=100, order_by='pubdate desc')
    rows=upcoming(records)
    if not rows:
        # Portal may include stale feeds; expose latest known items instead of pretending they are upcoming.
        records.sort(key=lambda r: str(r.get('pubdate','')), reverse=True)
        rows=records[:5]
    return [PingItem(str(r.get('title','untitled event')), str(r.get('description') or 'No description in feed'), r.get('pubdate'), r.get('link')) for r in rows]

def build_ping(): return render_ping('📅','Würzburg ZDI event digest', build_items())
def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv); items=build_items()
    if '--json' in argv: print(json.dumps([i.__dict__ for i in items], ensure_ascii=False, indent=2)); return 0
    text=render_ping('📅','Würzburg ZDI event digest',items)
    if '--send-telegram' in argv: send_telegram(text)
    else: print(text)
    return 0
if __name__=='__main__': raise SystemExit(main())
