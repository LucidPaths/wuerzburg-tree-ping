from wuerzburg_tree_ping.cli import (
    DATASETS,
    evaluate_climate_trees,
    evaluate_garden_soil,
    evaluate_water_barrels,
    render_alerts,
)


def test_climate_tree_alerts_on_low_vwc():
    alerts = evaluate_climate_trees([
        {
            "timestamp": "2026-06-22T07:14:27+00:00",
            "originatorname": "Grafeneckart 1",
            "ss_serialnumber": "sensor-a",
            "ss_baumart": "Platanus x hispanica",
            "vwc": 19,
        },
        {"ss_serialnumber": "sensor-b", "vwc": 47},
    ])

    assert len(alerts) == 1
    assert alerts[0].severity == "critical"
    assert alerts[0].dataset == DATASETS["climate_trees"]
    assert "Grafeneckart 1" in alerts[0].title


def test_garden_soil_alerts_on_low_30cm_moisture():
    alerts = evaluate_garden_soil([
        {
            "timestamp": "2026-06-22T09:19:54+00:00",
            "sensor_id": "soil-a",
            "standort": "Ahorn",
            "soil_moisture_30": 3.5,
            "soil_moisture_100": 3.8,
            "temperature_celsius": 29.3,
        }
    ])

    assert len(alerts) == 1
    assert alerts[0].severity == "critical"
    assert "Ahorn" in alerts[0].title
    assert "3.5%" in alerts[0].body


def test_water_barrel_alerts_when_low():
    alerts = evaluate_water_barrels([
        {"timestamp": "now", "sensor_id": "barrel-a", "standort": "Eichenfass", "level_percent": 20},
        {"timestamp": "now", "sensor_id": "barrel-b", "standort": "Fassadentonne", "level_percent": 80},
    ])

    assert len(alerts) == 1
    assert alerts[0].severity == "warning"
    assert "Eichenfass" in alerts[0].title


def test_render_alerts_empty_is_silent_for_cron():
    assert render_alerts([]) == ""


def test_render_alerts_contains_header_and_alert_text():
    alert = evaluate_garden_soil([
        {"sensor_id": "soil-a", "standort": "Ahorn", "soil_moisture_30": 3.5}
    ])[0]

    text = render_alerts([alert])

    assert "Würzburg OpenData watering ping" in text
    assert "Dry soil: Ahorn" in text
