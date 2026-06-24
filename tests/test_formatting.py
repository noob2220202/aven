from bot.flags import flag_emoji
from bot.formatting import format_kickoff_time, format_lineups, format_match_line, format_odds, format_status


def test_format_kickoff_time():
    assert format_kickoff_time("2026-06-25T01:00:00+00:00") == "10:00"


def test_format_status_not_started():
    status = {"short": "NS", "long": "Not Started", "elapsed": None}
    goals = {"home": None, "away": None}
    assert format_status(status, goals) == "경기 전"


def test_format_status_live_with_score():
    status = {"short": "2H", "long": "Second Half", "elapsed": 70}
    goals = {"home": 2, "away": 1}
    assert format_status(status, goals) == "🔴 후반전 2:1"


def test_format_status_finished():
    status = {"short": "FT", "long": "Match Finished", "elapsed": 90}
    goals = {"home": 3, "away": 0}
    assert format_status(status, goals) == "경기 종료 3:0"


def test_format_match_line_includes_flags_and_bold_names():
    fixture = {
        "teams": {"home": {"name": "Brazil"}, "away": {"name": "Argentina"}},
        "fixture": {
            "date": "2026-06-25T01:00:00+00:00",
            "status": {"short": "NS", "long": "Not Started", "elapsed": None},
        },
        "goals": {"home": None, "away": None},
    }
    line = format_match_line(fixture)
    assert flag_emoji("Brazil") in line
    assert flag_emoji("Argentina") in line
    assert "<b>Brazil</b>" in line
    assert "<b>Argentina</b>" in line
    assert "10:00" in line


def test_flag_emoji_known_and_unknown():
    assert flag_emoji("Brazil") == "🇧🇷"
    assert flag_emoji("South Korea") == "🇰🇷"
    assert flag_emoji("Atlantis") == "🏳️"


def test_format_lineups_empty():
    assert "라인업이 안 나왔어요" in format_lineups([])


def test_format_lineups_with_data():
    lineups = [
        {
            "team": {"name": "Brazil"},
            "coach": {"name": "Carlo Ancelotti"},
            "formation": "4-3-3",
            "startXI": [
                {"player": {"number": 1, "name": "Alisson", "pos": "G"}},
            ],
        }
    ]
    text = format_lineups(lineups)
    assert "Brazil" in text
    assert "4-3-3" in text
    assert "Alisson" in text
    assert flag_emoji("Brazil") in text


def test_format_odds_empty():
    assert "배당이 안 떴어요" in format_odds([])


def test_format_odds_with_data():
    odds_response = [
        {
            "bookmakers": [
                {
                    "name": "Bet365",
                    "bets": [
                        {
                            "name": "Match Winner",
                            "values": [
                                {"value": "Home", "odd": "1.85"},
                                {"value": "Draw", "odd": "3.40"},
                                {"value": "Away", "odd": "4.20"},
                            ],
                        }
                    ],
                }
            ]
        }
    ]
    text = format_odds(odds_response)
    assert "Bet365" in text
    assert "1.85" in text
