SUBDIVISION_FLAGS = {
    "england": "gbeng",
    "scotland": "gbsct",
    "wales": "gbwls",
}

COUNTRY_ISO2 = {
    # UEFA
    "france": "FR", "germany": "DE", "spain": "ES", "italy": "IT",
    "portugal": "PT", "netherlands": "NL", "belgium": "BE", "croatia": "HR",
    "switzerland": "CH", "poland": "PL", "serbia": "RS", "denmark": "DK",
    "sweden": "SE", "norway": "NO", "austria": "AT", "ukraine": "UA",
    "czech republic": "CZ", "czechia": "CZ", "slovakia": "SK", "slovenia": "SI",
    "hungary": "HU", "romania": "RO", "greece": "GR", "turkey": "TR",
    "iceland": "IS", "finland": "FI", "bosnia and herzegovina": "BA",
    "albania": "AL", "north macedonia": "MK", "georgia": "GE", "russia": "RU",
    "republic of ireland": "IE", "ireland": "IE", "northern ireland": "GB",
    # CONMEBOL
    "brazil": "BR", "argentina": "AR", "uruguay": "UY", "colombia": "CO",
    "ecuador": "EC", "paraguay": "PY", "chile": "CL", "peru": "PE",
    "bolivia": "BO", "venezuela": "VE",
    # CONCACAF
    "usa": "US", "united states": "US", "mexico": "MX", "canada": "CA",
    "costa rica": "CR", "jamaica": "JM", "panama": "PA", "honduras": "HN",
    "el salvador": "SV", "haiti": "HT", "curacao": "CW", "curaçao": "CW",
    "trinidad and tobago": "TT", "guatemala": "GT", "suriname": "SR",
    # CAF
    "morocco": "MA", "senegal": "SN", "tunisia": "TN", "algeria": "DZ",
    "egypt": "EG", "nigeria": "NG", "ghana": "GH", "cameroon": "CM",
    "ivory coast": "CI", "côte d'ivoire": "CI", "cote d'ivoire": "CI",
    "south africa": "ZA", "mali": "ML", "dr congo": "CD", "congo dr": "CD",
    "cape verde": "CV", "burkina faso": "BF", "guinea": "GN", "zambia": "ZM",
    "mozambique": "MZ", "gabon": "GA", "benin": "BJ", "uganda": "UG",
    "angola": "AO", "namibia": "NA",
    # AFC
    "japan": "JP", "south korea": "KR", "korea republic": "KR",
    "australia": "AU", "iran": "IR", "ir iran": "IR", "saudi arabia": "SA",
    "qatar": "QA", "iraq": "IQ", "united arab emirates": "AE", "uae": "AE",
    "uzbekistan": "UZ", "jordan": "JO", "china": "CN", "china pr": "CN",
    "oman": "OM", "bahrain": "BH", "kuwait": "KW", "indonesia": "ID",
    "vietnam": "VN", "thailand": "TH", "india": "IN",
    "north korea": "KP", "korea dpr": "KP", "kyrgyzstan": "KG",
    "palestine": "PS",
    # OFC
    "new zealand": "NZ", "fiji": "FJ", "new caledonia": "NC",
}


def _regional_indicator_flag(iso2: str) -> str:
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in iso2.upper())


def _subdivision_flag(code: str) -> str:
    tags = "".join(chr(0xE0000 + ord(c)) for c in code)
    return "\U0001F3F4" + tags + "\U000E007F"


def flag_emoji(team_name: str) -> str:
    key = team_name.strip().lower()
    if key in SUBDIVISION_FLAGS:
        return _subdivision_flag(SUBDIVISION_FLAGS[key])
    iso2 = COUNTRY_ISO2.get(key)
    if iso2:
        return _regional_indicator_flag(iso2)
    return "🏳️"
