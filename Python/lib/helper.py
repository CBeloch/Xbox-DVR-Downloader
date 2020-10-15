
import re

def clean_game_title(title: str) -> str:
    # only keep digits, word characters, dashes, underscores and whitespaces
    return re.sub("[^\d\w\-_\s]", '', title)
