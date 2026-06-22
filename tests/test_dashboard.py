from wuerzburg_tree_ping.dashboard import build_static_html, item_dict, text_card
from wuerzburg_tree_ping.common import PingItem


def test_dashboard_html_contains_live_endpoint():
    html = build_static_html()
    assert "OpenData Würzburg Possibilities" in html
    assert "/api/snapshot" in html
    assert "Refresh data" in html


def test_dashboard_static_html_embeds_snapshot():
    html = build_static_html({"generatedAt": "test", "cards": []})
    assert "window.__STATIC_SNAPSHOT__" in html
    assert '"generatedAt": "test"' in html


def test_dashboard_normalizes_ping_items():
    item = item_dict(PingItem("Title", "Body", "2099-01-01"))
    assert item["title"] == "Title"
    assert item["body"] == "Body"
    assert item["timestamp"] == "2099-01-01"


def test_dashboard_card_shape():
    card = text_card(
        key="demo",
        title="Demo",
        icon="•",
        folder="usecases/demo",
        dataset_ids=["dataset"],
        pitch="Demo pitch",
        items=[PingItem("A", "B")],
        metric_label="items",
    )
    assert card["value"] == 1
    assert card["items"][0]["title"] == "A"
