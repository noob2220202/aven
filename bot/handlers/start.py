from telegram import Update
from telegram.ext import ContextTypes

HELP_TEXT = (
    "⚽ *2026 월드컵 봇*\n\n"
    "/matches - 오늘(한국시간) 경기 목록\n"
    "/matches YYYY-MM-DD - 특정 날짜 경기 목록\n"
    "/help - 도움말\n\n"
    "경기 목록에서 경기를 선택하면 라인업 📋 / 배당 💰 / 코멘트 🗣 / 예측 🔮 을 확인할 수 있어요."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")
