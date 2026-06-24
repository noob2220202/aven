import html
from datetime import date, datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from .. import api_football, config
from ..flags import flag_emoji
from ..formatting import format_match_line


def build_matches_view(target_date: date, fixtures: list[dict]) -> tuple[str, InlineKeyboardMarkup]:
    weekday = ["월", "화", "수", "목", "금", "토", "일"][target_date.weekday()]
    lines = ["🏆 <b>2026 FIFA 월드컵</b>", f"🗓 <b>{target_date.isoformat()}</b> ({weekday}) · 한국시간 기준", ""]
    buttons = []

    if not fixtures:
        lines.append("😴 <i>이 날은 경기가 없는 휴식일이에요.</i>")
    else:
        for fixture in fixtures:
            lines.append(format_match_line(fixture))
            lines.append("")
            home = fixture["teams"]["home"]["name"]
            away = fixture["teams"]["away"]["name"]
            button_label = f"{flag_emoji(home)} {home} vs {away} {flag_emoji(away)}"
            buttons.append(
                [InlineKeyboardButton(button_label, callback_data=f"match:{fixture['fixture']['id']}")]
            )

    nav_row = [
        InlineKeyboardButton("◀ 전날", callback_data=f"date:{(target_date - timedelta(days=1)).isoformat()}"),
        InlineKeyboardButton("다음날 ▶", callback_data=f"date:{(target_date + timedelta(days=1)).isoformat()}"),
    ]
    buttons.append(nav_row)

    return "\n".join(lines).rstrip(), InlineKeyboardMarkup(buttons)


def _parse_target_date(args: list[str]) -> date:
    if not args:
        return datetime.now(config.KST).date()
    return datetime.strptime(args[0], "%Y-%m-%d").date()


async def matches_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        target_date = _parse_target_date(context.args)
    except ValueError:
        await update.message.reply_text("🤔 날짜 형식이 이상해요. <code>/matches 2026-06-25</code> 처럼 써주세요.", parse_mode="HTML")
        return

    status_message = await update.message.reply_text("🔍 경기 일정 찾아보는 중...")

    try:
        fixtures = await api_football.get_fixtures_by_kst_date(target_date)
    except api_football.ApiFootballError as exc:
        await status_message.edit_text(f"⚠️ 경기 정보를 못 가져왔어요: {html.escape(str(exc))}", parse_mode="HTML")
        return

    text, keyboard = build_matches_view(target_date, fixtures)
    await status_message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)


async def date_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    target_date = datetime.strptime(query.data.split(":", 1)[1], "%Y-%m-%d").date()

    try:
        fixtures = await api_football.get_fixtures_by_kst_date(target_date)
    except api_football.ApiFootballError as exc:
        await query.edit_message_text(f"⚠️ 경기 정보를 못 가져왔어요: {html.escape(str(exc))}", parse_mode="HTML")
        return

    text, keyboard = build_matches_view(target_date, fixtures)
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)
