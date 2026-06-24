import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from .. import ai_service, api_football
from ..api_football import to_kst_datetime
from ..formatting import format_kickoff_time, format_lineups, format_odds, format_odds_summary_for_prompt, format_status


def _detail_keyboard(fixture_id: int, kst_date: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📋 라인업", callback_data=f"lineup:{fixture_id}"),
                InlineKeyboardButton("💰 배당", callback_data=f"odds:{fixture_id}"),
            ],
            [
                InlineKeyboardButton("🗣 코멘트", callback_data=f"comment:{fixture_id}"),
                InlineKeyboardButton("🔮 예측", callback_data=f"predict:{fixture_id}"),
            ],
            [InlineKeyboardButton("◀ 목록으로", callback_data=f"date:{kst_date}")],
        ]
    )


def _format_detail(fixture: dict) -> str:
    home = fixture["teams"]["home"]["name"]
    away = fixture["teams"]["away"]["name"]
    kickoff = format_kickoff_time(fixture["fixture"]["date"])
    status = format_status(fixture["fixture"]["status"], fixture["goals"])
    venue = (fixture["fixture"].get("venue") or {}).get("name") or "미정"
    round_name = fixture.get("league", {}).get("round", "")

    return (
        f"🏆 {round_name}\n"
        f"🕐 {kickoff} (한국시간)\n"
        f"🏟 {venue}\n\n"
        f"*{home}* vs *{away}*\n"
        f"상태: {status}"
    )


async def _get_fixture_or_notify(query, fixture_id: int) -> dict | None:
    fixture = await api_football.get_fixture(fixture_id)
    if fixture is None:
        await query.edit_message_text("경기 정보를 찾을 수 없습니다.")
    return fixture


async def match_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    fixture_id = int(query.data.split(":", 1)[1])

    try:
        fixture = await _get_fixture_or_notify(query, fixture_id)
    except api_football.ApiFootballError as exc:
        await query.edit_message_text(f"경기 정보를 가져오지 못했습니다: {exc}")
        return
    if fixture is None:
        return

    kst_date = to_kst_datetime(fixture["fixture"]["date"]).date().isoformat()
    await query.edit_message_text(
        _format_detail(fixture), parse_mode="Markdown", reply_markup=_detail_keyboard(fixture_id, kst_date)
    )


async def lineup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer("라인업 조회 중...")
    fixture_id = int(query.data.split(":", 1)[1])

    try:
        fixture = await _get_fixture_or_notify(query, fixture_id)
        if fixture is None:
            return
        lineups = await api_football.get_lineups(fixture_id)
    except api_football.ApiFootballError as exc:
        await query.edit_message_text(f"라인업을 가져오지 못했습니다: {exc}")
        return

    kst_date = to_kst_datetime(fixture["fixture"]["date"]).date().isoformat()
    await query.edit_message_text(
        format_lineups(lineups), parse_mode="Markdown", reply_markup=_detail_keyboard(fixture_id, kst_date)
    )


async def odds_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer("배당 조회 중...")
    fixture_id = int(query.data.split(":", 1)[1])

    try:
        fixture = await _get_fixture_or_notify(query, fixture_id)
        if fixture is None:
            return
        odds = await api_football.get_odds(fixture_id)
    except api_football.ApiFootballError as exc:
        await query.edit_message_text(f"배당 정보를 가져오지 못했습니다: {exc}")
        return

    kst_date = to_kst_datetime(fixture["fixture"]["date"]).date().isoformat()
    await query.edit_message_text(
        format_odds(odds), parse_mode="Markdown", reply_markup=_detail_keyboard(fixture_id, kst_date)
    )


async def comment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer("코멘트 생성 중...")
    fixture_id = int(query.data.split(":", 1)[1])

    try:
        fixture = await _get_fixture_or_notify(query, fixture_id)
    except api_football.ApiFootballError as exc:
        await query.edit_message_text(f"경기 정보를 가져오지 못했습니다: {exc}")
        return
    if fixture is None:
        return

    home = fixture["teams"]["home"]["name"]
    away = fixture["teams"]["away"]["name"]
    kst_date = to_kst_datetime(fixture["fixture"]["date"]).date().isoformat()

    try:
        home_comment, away_comment = await asyncio.gather(
            ai_service.get_team_comment(home),
            ai_service.get_team_comment(away),
        )
    except ai_service.AiServiceError as exc:
        await query.edit_message_text(str(exc), reply_markup=_detail_keyboard(fixture_id, kst_date))
        return

    text = f"🗣 *{home}*\n{home_comment}\n\n🗣 *{away}*\n{away_comment}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=_detail_keyboard(fixture_id, kst_date))


async def predict_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer("예측 중...")
    fixture_id = int(query.data.split(":", 1)[1])

    try:
        fixture = await _get_fixture_or_notify(query, fixture_id)
    except api_football.ApiFootballError as exc:
        await query.edit_message_text(f"경기 정보를 가져오지 못했습니다: {exc}")
        return
    if fixture is None:
        return

    home = fixture["teams"]["home"]["name"]
    away = fixture["teams"]["away"]["name"]
    kst_date = to_kst_datetime(fixture["fixture"]["date"]).date().isoformat()

    context_note = ""
    try:
        odds = await api_football.get_odds(fixture_id)
        context_note = format_odds_summary_for_prompt(odds)
    except api_football.ApiFootballError:
        pass

    try:
        prediction = await ai_service.predict_match(home, away, context_note)
    except ai_service.AiServiceError as exc:
        await query.edit_message_text(str(exc), reply_markup=_detail_keyboard(fixture_id, kst_date))
        return

    text = f"🔮 *예측 결과*\n\n{prediction}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=_detail_keyboard(fixture_id, kst_date))
