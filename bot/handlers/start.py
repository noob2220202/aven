from telegram import Update
from telegram.ext import ContextTypes

HELP_TEXT = (
    "⚽️ <b>2026 월드컵 봇</b>이 왔습니다!\n\n"
    "🗓 /matches — 오늘(한국시간) 경기 목록\n"
    "🗓 /matches 2026-06-25 — 특정 날짜 경기 목록\n"
    "❓ /help — 도움말\n\n"
    "경기를 고르면 아래 메뉴로 더 깊게 파볼 수 있어요.\n"
    "📋 라인업 · 💰 배당 · 🗣 코멘트 · 🔮 예측"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="HTML")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="HTML")
