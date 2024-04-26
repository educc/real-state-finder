def to_number(string: str) -> float:
    # pick only numbers and dot
    return float("".join([char for char in string if char.isdigit() or char == "."]))


def encode_url(url: str) -> str:
    # use urllib.parse.quote
    return url


def month_number_from_es_name(month_name_es: str) -> int:
    # use a dictionary
    return {
        "enero": 1,
        "febrero": 2,
        "marzo": 3,
        "abril": 4,
        "mayo": 5,
        "junio": 6,
        "julio": 7,
        "agosto": 8,
        "septiembre": 9,
        "octubre": 10,
        "noviembre": 11,
        "diciembre": 12,
    }[month_name_es]
