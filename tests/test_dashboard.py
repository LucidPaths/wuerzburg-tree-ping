from wuerzburg_tree_ping.dashboard import (
    build_chat_messages,
    build_static_html,
    chat_answer_from_response,
    item_dict,
    ollama_chat_request,
    opendata_context,
    text_card,
)
from wuerzburg_tree_ping.common import PingItem


def test_dashboard_html_contains_live_endpoint():
    html = build_static_html()
    assert "OpenData Würzburg Possibilities" in html
    assert "/api/snapshot" in html
    assert "/api/chat" in html
    assert "Ask the OpenData assistant" in html
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


def sample_snapshot():
    return {
        "generatedAt": "2099-01-01 00:00 UTC",
        "source": "https://opendata.wuerzburg.de/",
        "cards": [
            text_card(
                key="parking",
                title="Parking",
                icon="P",
                folder="usecases/parking",
                dataset_ids=["parkplatzdaten_wuerzburg"],
                pitch="Parking pitch",
                items=[PingItem("Garage A", "frei", "2099")],
                metric_label="items",
            )
        ],
    }


def test_chat_context_is_scoped_to_snapshot():
    snapshot = sample_snapshot()
    context = opendata_context(snapshot)
    assert "Garage A" in context
    assert "parkplatzdaten_wuerzburg" in context
    messages = build_chat_messages("What is free?", snapshot)
    assert messages[0]["role"] == "system"
    assert "Do not invent" in messages[0]["content"]
    assert "Garage A" in messages[1]["content"]


def test_ollama_cloud_v1_uses_openai_compatible_chat_completions(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "https://ollama.com/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "demo-model")
    monkeypatch.delenv("OLLAMA_API_URL", raising=False)
    api_url, payload = ollama_chat_request("What is free?", sample_snapshot())
    assert api_url == "https://ollama.com/v1/chat/completions"
    assert payload["model"] == "demo-model"
    assert payload["temperature"] == 0.2
    assert "options" not in payload


def test_native_ollama_uses_api_chat_payload(monkeypatch):
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.delenv("OLLAMA_API_URL", raising=False)
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    api_url, payload = ollama_chat_request("What is free?", sample_snapshot())
    assert api_url == "http://127.0.0.1:11434/api/chat"
    assert payload["options"] == {"temperature": 0.2}


def test_chat_answer_from_native_and_openai_compatible_responses():
    assert chat_answer_from_response({"message": {"content": "native"}}) == "native"
    assert chat_answer_from_response({"choices": [{"message": {"content": "compat"}}]}) == "compat"
