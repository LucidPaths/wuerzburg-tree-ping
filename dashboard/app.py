from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wuerzburg_tree_ping.dashboard import (  # noqa: F401
    DEFAULT_HOST,
    DEFAULT_PORT,
    DASHBOARD_HTML,
    DashboardHandler,
    build_static_html,
    chat_with_ollama,
    collect_snapshot,
    connect_ai,
    item_dict,
    load_env_file,
    opendata_context,
    ai_status,
    main,
    ping_items,
    run_server,
    text_card,
)


if __name__ == "__main__":
    raise SystemExit(main())
