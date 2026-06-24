from datetime import date

from bot.api_football import kst_date_to_utc_range, to_kst_datetime


def test_kst_date_to_utc_range_within_single_utc_day():
    # 2026-06-25 12:00 KST -> well within a single UTC day (2026-06-25 03:00 UTC)
    utc_start, utc_end = kst_date_to_utc_range(date(2026, 6, 25))
    assert utc_start == date(2026, 6, 24)
    assert utc_end == date(2026, 6, 25)


def test_kst_date_to_utc_range_spans_two_utc_days():
    # KST day 2026-06-25 00:00~23:59 corresponds to UTC 2026-06-24 15:00 ~ 2026-06-25 14:59
    utc_start, utc_end = kst_date_to_utc_range(date(2026, 6, 25))
    assert utc_start < utc_end


def test_to_kst_datetime_converts_utc_offset_correctly():
    # 2026-06-25T16:00:00+00:00 UTC -> 2026-06-26 01:00 KST (UTC+9)
    dt = to_kst_datetime("2026-06-25T16:00:00+00:00")
    assert dt.strftime("%Y-%m-%d %H:%M") == "2026-06-26 01:00"
