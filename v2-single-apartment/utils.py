def to_number(string: str) -> float:
    # pick only numbers and dot
    return float("".join([char for char in string if char.isdigit() or char == "."]))


def encode_url(url: str) -> str:
    # use urllib.parse.quote
    return url
