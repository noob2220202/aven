# 월드컵 텔레그램 봇

2026 FIFA 월드컵 경기 정보를 텔레그램으로 확인하는 봇입니다.

## 기능

1. 한국 시간(KST) 기준 날짜별 경기 목록 (`/matches`)
2. 경기별 라인업 조회
3. 경기별 배당(승무패) 조회
4. 각 국가 대표팀에 대한 AI 코멘트 (OpenAI GPT)
5. 승자 및 스코어 예측 (OpenAI GPT)

## 데이터 소스

- 경기 일정 / 라인업 / 배당: [API-Football](https://www.api-football.com) 무료 플랜
  - 가입만 하면 무료로 사용 가능 (일 100회 호출 제한)
  - 라인업은 보통 킥오프 1시간 전, 배당은 경기 1~14일 전부터 제공됩니다
  - 무료 플랜 호출 제한 때문에 봇 내부적으로 응답을 잠시 캐싱합니다 (경기 목록 5분, 라인업/경기정보 2분, 배당 10분)
- 코멘트 / 예측: OpenAI GPT API

## 준비물

1. **텔레그램 봇 토큰**: [@BotFather](https://t.me/BotFather)에게 `/newbot`으로 발급
2. **API-Football 키**: https://www.api-football.com 가입 후 대시보드에서 무료 발급
3. **OpenAI API 키**: https://platform.openai.com 에서 발급

## 설치 및 실행

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# .env 파일에 토큰/키 입력

python -m bot.main
```

## 환경 변수

`.env.example` 참고:

| 변수 | 설명 |
|---|---|
| `TELEGRAM_BOT_TOKEN` | 텔레그램 봇 토큰 (필수) |
| `API_FOOTBALL_KEY` | API-Football 키 (필수, 경기/라인업/배당 기능에 사용) |
| `OPENAI_API_KEY` | OpenAI 키 (필수, 코멘트/예측 기능에 사용) |
| `OPENAI_MODEL` | 사용할 GPT 모델 (기본값: `gpt-4o-mini`) |
| `WORLDCUP_LEAGUE_ID` | API-Football 기준 월드컵 리그 ID (기본값: `1`) |
| `WORLDCUP_SEASON` | 대회 시즌(개최 연도, 기본값: `2026`) |

## 사용법

- `/start`, `/help` — 명령어 안내
- `/matches` — 오늘(한국시간) 경기 목록
- `/matches 2026-06-25` — 특정 날짜 경기 목록

경기 목록에서 경기를 선택하면 아래 버튼으로 세부 정보를 확인할 수 있습니다.

- 📋 라인업
- 💰 배당
- 🗣 코멘트 (양 팀 국가에 대한 짧은 AI 코멘트)
- 🔮 예측 (승자 + 예상 스코어, AI 생성)

## 테스트

```bash
pip install -r requirements-dev.txt
pytest
```

타임존 변환 및 텍스트 포맷팅 로직에 대한 단위 테스트만 포함되어 있으며, 외부 API(API-Football, OpenAI) 호출은 실제 키가 필요해 테스트 대상에서 제외했습니다.
