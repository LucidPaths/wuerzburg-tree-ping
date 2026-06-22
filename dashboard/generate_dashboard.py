from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from wuerzburg_tree_ping.dashboard import build_static_html, collect_snapshot


def main() -> int:
    out = Path(__file__).with_name("index.html")
    snapshot = collect_snapshot()
    out.write_text(build_static_html(snapshot), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
