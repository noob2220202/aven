from datetime import date, datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from .. import api_football, config
from ..formatting import format_kickoff_time, format_status


def build_matches_view(target_date: date, fixtures: list[dict]) -> tuple[str, InlineKeyboardMarkup]:
    lines = [f"📅 *{target_date.strftime('%Y-%m-%d')} 경기 일정 (한국시간)*", ""]
    buttons = []

    if not fixtures:
        lines.append("해당 날짜에 예정된 월드컵 경기가 없습니다.")
    else:
        for fixture in fixtures:
            home = fixture["teams"]["home"]["name"]
            away = fixture["teams"]["away"]["name"]
            kickoff = format_kickoff_time(fixture["fixture"]["date"])
            status = format_status(fixture["fixture"]["status"], fixture["goals"])
            lines.append(f"{kickoff} | {home} vs {away} ({status})")
            buttons.append(
                [InlineKeyboardButton(f"{home} vs {away}", callback_data=f"match:{fixture['fixture']['id']}")]
            )

    nav_row = [
        InlineKeyboardButton("◀ 전날", callback_data=f"date:{(target_date - timedelta(days=1)).isoformat()}"),
        InlineKeyboardButton("다음날 ▶", callback_data=f"date:{(target_date + timedelta(days=1)).isoformat()}"),
    ]
    buttons.append(nav_row)

    return "\n".join(lines), InlineKeyboardMarkup(buttons)


def _parse_target_date(args: list[str]) -> date:
    if not args:
        return datetime.now(config.KST).date()
    return datetime.strptime(args[0], "%Y-%m-%d").date()


async def matches_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        target_date = _parse_target_date(context.args)
    except ValueError:
        await update.message.reply_text("날짜 형식이 올바르지 않습니다. 예: /matches 2026-06-25")
        return

    status_message = await update.message.reply_text("경기 일정을 조회 중입니다...")

    try:
        fixtures = await api_football.get_fixtures_by_kst_date(target_date)
    except api_football.ApiFootballError as exc:
        await status_message.edit_text(f"경기 정보를 가져오지 못했습니다: {exc}")
        return

    text, keyboard = build_matches_view(target_date, fixtures)
    await status_message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def date_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    target_date = datetime.strptime(query.data.split(":", 1)[1], "%Y-%m-%d").date()

    try:
        fixtures = await api_football.get_fixtures_by_kst_date(target_date)
    except api_football.ApiFootballError as exc:
        await query.edit_message_text(f"경기 정보를 가져오지 못했습니다: {exc}")
        return

    text, keyboard = build_matches_view(target_date, fixtures)
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
