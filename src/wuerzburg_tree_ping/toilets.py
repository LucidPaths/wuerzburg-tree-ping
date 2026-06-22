from __future__ import annotations
import json, sys
from .common import PingItem, fetch_records, haversine_km, render_ping, send_telegram
DATASET_ID='barrierefreie-toiletten-im-stadtgebiet-wuerzburg'
DEFAULT_LAT=49.7939; DEFAULT_LON=9.9300

def nearest(records, lat=DEFAULT_LAT, lon=DEFAULT_LON, limit=5):
    rows=[]
    for r in records:
        p=r.get('geo_point_2d') or {}; plat=p.get('lat'); plon=p.get('lon')
        if isinstance(plat,(int,float)) and isinstance(plon,(int,float)):
            rows.append((haversine_km(lat,lon,plat,plon),r))
    rows.sort(key=lambda x:x[0]); return rows[:limit]

def build_items(records=None, lat=DEFAULT_LAT, lon=DEFAULT_LON):
    records = records if records is not None else fetch_records(DATASET_ID, limit=100)
    items=[]
    for dist,r in nearest(records,lat,lon):
        desc=str(r.get('description') or '').replace('\n',' ')[:180]
        body=f"{dist:.2f} km away. Type: {r.get('toilettype','unknown')}. {desc}".strip()
        items.append(PingItem(str(r.get('company') or r.get('id')), body))
    return items

def build_ping(lat=DEFAULT_LAT, lon=DEFAULT_LON): return render_ping('♿','Nearest accessible toilets', build_items(lat=lat,lon=lon))
def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv); lat=DEFAULT_LAT; lon=DEFAULT_LON
    if '--lat' in argv and '--lon' in argv:
        lat=float(argv[argv.index('--lat')+1]); lon=float(argv[argv.index('--lon')+1])
    items=build_items(lat=lat,lon=lon)
    if '--json' in argv: print(json.dumps([i.__dict__ for i in items], ensure_ascii=False, indent=2)); return 0
    text=render_ping('♿','Nearest accessible toilets',items)
    if '--send-telegram' in argv: send_telegram(text)
    else: print(text)
    return 0
if __name__=='__main__': raise SystemExit(main())
