from __future__ import annotations
from datetime import date
import json, sys
from .common import PingItem, fetch_records, render_ping, send_telegram
DATASET_ID='abfallkalender-wuerzburg'

def upcoming(records, district=None, limit=8):
    today=date.today().isoformat()
    rows=[r for r in records if str(r.get('start',''))>=today]
    if district:
        d=district.lower()
        rows=[r for r in rows if d in str(r.get('stadtteil_name','')).lower() or d in str(r.get('kurztext','')).lower()]
    rows.sort(key=lambda r: (str(r.get('start','')), str(r.get('stadtteil_name','')), str(r.get('titel',''))))
    return rows[:limit]

def build_items(records=None, district=None):
    records = records if records is not None else fetch_records(DATASET_ID, limit=100, order_by='start desc')
    return [PingItem(f"{r.get('start')} — {r.get('titel')} ({r.get('stadtteil_name','unknown district')})", str(r.get('kurztext') or r.get('kategorie') or 'Waste pickup'), r.get('start')) for r in upcoming(records, district)]

def build_ping(district=None): return render_ping('🗑️','Würzburg waste pickup reminder', build_items(district=district), empty_text='')
def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv); district=None
    if '--district' in argv:
        i=argv.index('--district'); district=argv[i+1] if i+1 < len(argv) else None
    items=build_items(district=district)
    if '--json' in argv: print(json.dumps([i.__dict__ for i in items], ensure_ascii=False, indent=2)); return 0
    text=render_ping('🗑️','Würzburg waste pickup reminder',items)
    if '--send-telegram' in argv: send_telegram(text)
    else: print(text)
    return 0
if __name__=='__main__': raise SystemExit(main())
