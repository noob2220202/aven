import time
from typing import Optional

from openai import AsyncOpenAI

from . import config

_client: Optional[AsyncOpenAI] = None
_cache: dict[str, tuple[float, str]] = {}
_CACHE_TTL = 3600

SYSTEM_PROMPT = "너는 축구 전문 해설가다. 한국어로 간결하고 흥미롭게 답한다."


class AiServiceError(Exception):
    pass


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
    return _client


async def _chat(prompt: str, cache_key: str) -> str:
    if not config.OPENAI_API_KEY:
        raise AiServiceError("OPENAI_API_KEY가 설정되지 않았습니다.")

    cached = _cache.get(cache_key)
    if cached is not None and time.monotonic() - cached[0] < _CACHE_TTL:
        return cached[1]

    client = _get_client()
    try:
        response = await client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            max_tokens=300,
        )
    except Exception as exc:  # openai SDK raises various subclasses of OpenAIError
        raise AiServiceError(f"OpenAI 요청 중 오류가 발생했습니다: {exc}") from exc

    text = (response.choices[0].message.content or "").strip()
    _cache[cache_key] = (time.monotonic(), text)
    return text


async def get_team_comment(team_name: str) -> str:
    prompt = (
        f"2026 FIFA 월드컵에 출전한 '{team_name}' 대표팀에 대해 "
        "3문장 이내로 간단한 코멘트를 작성해줘. 팀의 강점, 스타일, 주목할 점을 포함해줘."
    )
    return await _chat(prompt, cache_key=f"comment:{team_name}")


async def predict_match(home_team: str, away_team: str, context_note: str = "") -> str:
    context_line = f"\n{context_note}" if context_note else ""
    prompt = (
        f"2026 FIFA 월드컵 경기 '{home_team} vs {away_team}'의 결과를 예측해줘."
        f"{context_line}\n"
        "승자와 예상 스코어를 먼저 한 줄로 명확히 제시하고, "
        "이어서 2문장 이내로 간단한 근거를 한국어로 작성해줘."
    )
    return await _chat(prompt, cache_key=f"predict:{home_team}:{away_team}")
