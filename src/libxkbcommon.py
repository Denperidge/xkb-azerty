from .shared import clone_or_pull_repo
from pathlib import Path
from re import findall, match

UPSTREAM = "https://github.com/xkbcommon/libxkbcommon.git";
DIR_LIBXKBCOMMON = Path("vendor/libxkbcommon");

FILE_KEYSYMS = DIR_LIBXKBCOMMON.joinpath("include/xkbcommon/xkbcommon-keysyms.h")

REGEX_GET_ALIAS = r"XKB_KEY_(?P<alias>\w*) +(?P<unicode>[0-9a-z]+)"

characters: dict[str, str] = {}

# This runs when importing the file as well
def init():
    _ = clone_or_pull_repo(UPSTREAM, DIR_LIBXKBCOMMON)

    contents: str = FILE_KEYSYMS.read_text("utf-8")

    entries: list[tuple[str,str]] = findall(REGEX_GET_ALIAS, contents)
    for entry in entries:
        reformat = entry[1].replace('0x', r'\u')
        characters[entry[0]] = (reformat.encode("utf-8")).decode("unicode-escape")

r"""
input: "ampersand"
output: "\u0026"

"""
def xkb_alias_to_character(alias: str):
    return characters[alias]

init()
