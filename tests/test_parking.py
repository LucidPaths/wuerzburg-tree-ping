from wuerzburg_tree_ping.parking import latest_per_parking, summarize


def test_latest_per_parking_keeps_newest_first():
    statuses = latest_per_parking([
        {"id": 1, "name": "PH Bahnhof", "status": "frei", "values_from": "new"},
        {"id": 1, "name": "PH Bahnhof", "status": "belegt", "values_from": "old"},
        {"id": 2, "name": "Juliusspital", "status": "belegt", "values_from": "new"},
    ])

    assert [status.name for status in statuses] == ["PH Bahnhof", "Juliusspital"]
    assert statuses[0].status == "frei"


def test_summarize_parking_lists_blocked_and_free_options():
    statuses = latest_per_parking([
        {"id": 1, "name": "Juliusspital", "status": "belegt", "values_from": "2026-06-22T11:50:01+00:00"},
        {"id": 2, "name": "Marktgarage", "status": "frei", "values_from": "2026-06-22T11:50:00+00:00"},
    ])

    text = summarize(statuses)

    assert "Würzburg parking ping" in text
    assert "Juliusspital: belegt" in text
    assert "Marktgarage: frei" in text
