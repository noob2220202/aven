import time
from typing import Optional

from openai import AsyncOpenAI

from . import config

_client: Optional[AsyncOpenAI] = None
_cache: dict[str, tuple[float, str]] = {}
_CACHE_TTL = 3600

SYSTEM_PROMPT = (
    "너는 한국 스포츠 채널의 축구 캐스터야. 방송에서 바로 말하듯 자연스럽고 "
    "확신 있는 캐주얼한 구어체로 답해. '또한', '결론적으로', '전반적으로', "
    "'~라고 할 수 있습니다' 같은 딱딱하고 뻔한 AI식 표현은 절대 쓰지 마. "
    "별표나 마크다운 기호, 글머리 기호 없이 순수 텍스트로만 짧게 답해."
)


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
        f"2026 월드컵에 나온 '{team_name}' 대표팀, 친한 사람한테 말해주듯 2~3문장으로 "
        "짧게 평가해줘. 전력이나 스타일, 눈에 띄는 포인트 하나 정도를 자연스럽게 녹여서 "
        "캐스터처럼 입담 있게 말해줘."
    )
    return await _chat(prompt, cache_key=f"comment:{team_name}")


async def predict_match(home_team: str, away_team: str, context_note: str = "") -> str:
    context_line = f"\n{context_note}" if context_note else ""
    prompt = (
        f"2026 월드컵 '{home_team} vs {away_team}' 경기, 진짜 캐스터처럼 자신 있게 승부를 "
        f"찍어줘.{context_line}\n"
        "첫 줄에 예상 스코어와 승자를 짧고 임팩트 있게 던지고, 바로 이어서 1~2문장으로 "
        "그렇게 보는 이유를 캐주얼하게 설명해줘."
    )
    return await _chat(prompt, cache_key=f"predict:{home_team}:{away_team}")
