from wuerzburg_tree_ping.bike import build_items as bike_items
from wuerzburg_tree_ping.pedestrian import build_items as pedestrian_items
from wuerzburg_tree_ping.waste import build_items as waste_items
from wuerzburg_tree_ping.toilets import build_items as toilet_items
from wuerzburg_tree_ping.events import build_items as event_items


def test_bike_counter_orders_latest_day_by_count():
    items = bike_items([
        {"dayofyear": "2026-06-19", "count": 9999, "name": "old"},
        {"dayofyear": "2026-06-20", "count": 10, "name": "quiet"},
        {"dayofyear": "2026-06-20", "count": 50, "name": "busy"},
    ])
    assert items[0].title == "busy"
    assert "50" in items[0].body


def test_pedestrian_pulse_orders_latest_day_by_count():
    items = pedestrian_items([
        {"timestamp": "2026-05-16", "pedestrians_count": 9999, "location_name": "old"},
        {"timestamp": "2026-05-17", "pedestrians_count": 100, "location_name": "low"},
        {"timestamp": "2026-05-17", "pedestrians_count": 500, "location_name": "high"},
    ])
    assert items[0].title == "high"
    assert "500" in items[0].body


def test_waste_reminder_filters_district():
    items = waste_items([
        {"start": "2099-01-01", "titel": "Papier", "stadtteil_name": "Grombühl", "kurztext": "Papier Grombühl"},
        {"start": "2099-01-01", "titel": "Bio", "stadtteil_name": "Heidingsfeld", "kurztext": "Bio Heidingsfeld"},
    ], district="Grombühl")
    assert len(items) == 1
    assert "Grombühl" in items[0].title


def test_toilets_nearest_uses_distance():
    items = toilet_items([
        {"company": "far", "toilettype": "WC", "geo_point_2d": {"lat": 50.0, "lon": 10.0}},
        {"company": "near", "toilettype": "WC", "geo_point_2d": {"lat": 49.7939, "lon": 9.9301}},
    ], lat=49.7939, lon=9.9300)
    assert items[0].title == "near"


def test_events_prefers_upcoming_but_falls_back_to_latest():
    items = event_items([
        {"title": "old", "pubdate": "2020-01-01T00:00:00+00:00", "description": None, "link": "x"},
        {"title": "newer", "pubdate": "2025-01-01T00:00:00+00:00", "description": None, "link": "y"},
    ])
    assert items[0].title == "newer"
