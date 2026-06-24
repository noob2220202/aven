import time
from datetime import date, datetime, timedelta
from typing import Any, Optional

import httpx

from . import config

_cache: dict[str, tuple[float, Any]] = {}


def _cache_get(key: str, ttl: float) -> Any:
    entry = _cache.get(key)
    if entry is None:
        return None
    timestamp, value = entry
    if time.monotonic() - timestamp > ttl:
        return None
    return value


def _cache_set(key: str, value: Any) -> None:
    _cache[key] = (time.monotonic(), value)


class ApiFootballError(Exception):
    pass


def to_kst_datetime(iso_date_str: str) -> datetime:
    return datetime.fromisoformat(iso_date_str).astimezone(config.KST)


def kst_date_to_utc_range(target_date: date) -> tuple[date, date]:
    """target_date(KST 기준 하루)를 커버하는 UTC 날짜 범위를 반환한다."""
    kst_start = datetime.combine(target_date, datetime.min.time(), tzinfo=config.KST)
    kst_end = kst_start + timedelta(days=1) - timedelta(seconds=1)
    utc_start = kst_start.astimezone(config.UTC).date()
    utc_end = kst_end.astimezone(config.UTC).date()
    return utc_start, utc_end


async def _get(endpoint: str, params: dict) -> list[dict]:
    if not config.API_FOOTBALL_KEY:
        raise ApiFootballError("API_FOOTBALL_KEY가 설정되지 않았습니다.")

    url = f"{config.API_FOOTBALL_BASE_URL}/{endpoint}"
    headers = {"x-apisports-key": config.API_FOOTBALL_KEY}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, headers=headers, params=params)
    except httpx.HTTPError as exc:
        raise ApiFootballError(f"API-Football 요청 중 오류가 발생했습니다: {exc}") from exc

    if response.status_code != 200:
        raise ApiFootballError(f"API-Football 요청 실패 (status={response.status_code})")

    payload = response.json()
    errors = payload.get("errors")
    if errors:
        raise ApiFootballError(f"API-Football 오류: {errors}")

    return payload.get("response", [])


async def get_fixtures_by_kst_date(target_date: date) -> list[dict]:
    """target_date(한국시간 기준) 하루 동안의 월드컵 경기 목록을 반환한다."""
    cache_key = f"fixtures:{target_date.isoformat()}"
    cached = _cache_get(cache_key, ttl=300)
    if cached is not None:
        return cached

    utc_start, utc_end = kst_date_to_utc_range(target_date)
    fixtures = await _get(
        "fixtures",
        {
            "league": config.WORLDCUP_LEAGUE_ID,
            "season": config.WORLDCUP_SEASON,
            "from": utc_start.isoformat(),
            "to": utc_end.isoformat(),
        },
    )

    result = [f for f in fixtures if to_kst_datetime(f["fixture"]["date"]).date() == target_date]
    result.sort(key=lambda f: f["fixture"]["date"])
    _cache_set(cache_key, result)
    return result


async def get_fixture(fixture_id: int) -> Optional[dict]:
    cache_key = f"fixture:{fixture_id}"
    cached = _cache_get(cache_key, ttl=120)
    if cached is not None:
        return cached

    fixtures = await _get("fixtures", {"id": fixture_id})
    result = fixtures[0] if fixtures else None
    if result is not None:
        _cache_set(cache_key, result)
    return result


async def get_lineups(fixture_id: int) -> list[dict]:
    cache_key = f"lineups:{fixture_id}"
    cached = _cache_get(cache_key, ttl=120)
    if cached is not None:
        return cached

    result = await _get("fixtures/lineups", {"fixture": fixture_id})
    _cache_set(cache_key, result)
    return result


async def get_odds(fixture_id: int) -> list[dict]:
    cache_key = f"odds:{fixture_id}"
    cached = _cache_get(cache_key, ttl=600)
    if cached is not None:
        return cached

    result = await _get("odds", {"fixture": fixture_id})
    _cache_set(cache_key, result)
    return result
