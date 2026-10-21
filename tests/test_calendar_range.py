"""get_calendar_items_for_range: the days asked for, each item once (no network: months are stubbed)."""

import garminconnect


def _client(months: dict) -> garminconnect.Garmin:
    client = garminconnect.Garmin()
    client.get_calendar_month = lambda year, month: {"calendarItems": months.get((year, month), [])}
    return client


def test_a_workout_scheduled_on_two_days_is_two_items():
    october = [
        {"itemType": "workout", "id": 11, "workoutId": 7, "date": "2026-10-06"},
        {"itemType": "workout", "id": 12, "workoutId": 7, "date": "2026-10-13"},
    ]
    items = _client({(2026, 10): october}).get_calendar_items_for_range("2026-10-01", "2026-10-31")
    assert [i["id"] for i in items] == [11, 12]


def test_an_item_shown_in_two_months_comes_once():
    race = {"itemType": "event", "id": None, "shareableEventUuid": "u", "date": "2026-10-31", "title": "Race"}
    run = {"itemType": "activity", "id": 5, "date": "2026-10-31"}
    months = {(2026, 10): [race, run], (2026, 11): [dict(race), dict(run)]}
    items = _client(months).get_calendar_items_for_range("2026-10-01", "2026-11-30")
    assert len(items) == 2


def test_an_activity_and_a_workout_with_the_same_id_are_two_items():
    october = [
        {"itemType": "activity", "id": 5, "date": "2026-10-06"},
        {"itemType": "workout", "id": 5, "workoutId": 9, "date": "2026-10-06"},
    ]
    items = _client({(2026, 10): october}).get_calendar_items_for_range("2026-10-01", "2026-10-31")
    assert len(items) == 2


def test_only_the_days_asked_for():
    october = [{"itemType": "activity", "id": 1, "date": "2026-09-28"},
               {"itemType": "activity", "id": 2, "date": "2026-10-02"}]
    items = _client({(2026, 10): october}).get_calendar_items_for_range("2026-10-01", "2026-10-31")
    assert [i["id"] for i in items] == [2]
