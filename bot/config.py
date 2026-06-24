import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "")
API_FOOTBALL_BASE_URL = os.getenv("API_FOOTBALL_BASE_URL", "https://v3.football.api-sports.io")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
WORLDCUP_LEAGUE_ID = int(os.getenv("WORLDCUP_LEAGUE_ID", "1"))
WORLDCUP_SEASON = int(os.getenv("WORLDCUP_SEASON", "2026"))

KST = ZoneInfo("Asia/Seoul")
UTC = ZoneInfo("UTC")


def validate() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN 환경변수가 설정되지 않았습니다. .env 파일을 확인하세요."
        )
