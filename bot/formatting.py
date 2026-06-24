from .api_football import to_kst_datetime

STATUS_KO = {
    "TBD": "일정 미정",
    "NS": "경기 전",
    "1H": "전반전",
    "HT": "하프타임",
    "2H": "후반전",
    "ET": "연장전",
    "BT": "연장 휴식",
    "P": "승부차기",
    "FT": "경기 종료",
    "AET": "연장 종료",
    "PEN": "승부차기 종료",
    "SUSP": "경기 중단",
    "INT": "경기 중단",
    "PST": "연기",
    "CANC": "취소",
    "ABD": "중단",
    "AWD": "몰수",
    "WO": "부전승",
    "LIVE": "진행중",
}

LIVE_STATUSES = {"1H", "2H", "ET", "BT", "P", "LIVE"}


def format_kickoff_time(iso_date_str: str) -> str:
    return to_kst_datetime(iso_date_str).strftime("%H:%M")


def format_status(status: dict, goals: dict) -> str:
    short = status.get("short", "")
    label = STATUS_KO.get(short, short or "정보 없음")
    if short in LIVE_STATUSES:
        label = f"🔴 {label}"

    home_goals = goals.get("home")
    away_goals = goals.get("away")
    if home_goals is not None and away_goals is not None:
        return f"{label} {home_goals}-{away_goals}"
    return label


def format_lineups(lineups: list[dict]) -> str:
    if not lineups:
        return "⏳ 라인업이 아직 발표되지 않았습니다. (보통 경기 시작 1시간 전 공개됩니다)"

    blocks = []
    for team_lineup in lineups:
        team_name = team_lineup.get("team", {}).get("name", "알 수 없는 팀")
        formation = team_lineup.get("formation") or "포메이션 미정"
        coach = team_lineup.get("coach", {}).get("name") or "감독 미정"
        starters = team_lineup.get("startXI", [])
        starter_lines = [
            f"  {p['player'].get('number', '-')}. {p['player'].get('name', '?')} "
            f"({p['player'].get('pos', '?')})"
            for p in starters
        ]
        block = f"*{team_name}* ({formation})\n감독: {coach}\n" + "\n".join(starter_lines)
        blocks.append(block)
    return "\n\n".join(blocks)


def format_odds(odds_response: list[dict]) -> str:
    if not odds_response:
        return "⏳ 아직 배당 정보가 제공되지 않습니다. (보통 경기 1~14일 전 공개됩니다)"

    bookmakers = odds_response[0].get("bookmakers", [])
    lines = ["💰 *승무패 배당 (Match Winner)*", ""]
    for bookmaker in bookmakers[:3]:
        bet = next((b for b in bookmaker.get("bets", []) if b.get("name") == "Match Winner"), None)
        if not bet:
            continue
        values = {v["value"]: v["odd"] for v in bet.get("values", [])}
        lines.append(
            f"*{bookmaker.get('name', '북메이커')}*  "
            f"승 {values.get('Home', '-')} / 무 {values.get('Draw', '-')} / 패 {values.get('Away', '-')}"
        )

    if len(lines) == 2:
        return "⏳ 아직 배당 정보가 제공되지 않습니다. (보통 경기 1~14일 전 공개됩니다)"
    return "\n".join(lines)


def format_odds_summary_for_prompt(odds_response: list[dict]) -> str:
    if not odds_response:
        return ""

    bookmakers = odds_response[0].get("bookmakers", [])
    if not bookmakers:
        return ""

    bet = next((b for b in bookmakers[0].get("bets", []) if b.get("name") == "Match Winner"), None)
    if not bet:
        return ""

    values = {v["value"]: v["odd"] for v in bet.get("values", [])}
    return (
        f"참고용 배당(낮을수록 우세): 홈 승 {values.get('Home', '-')}, "
        f"무승부 {values.get('Draw', '-')}, 원정 승 {values.get('Away', '-')}"
    )
