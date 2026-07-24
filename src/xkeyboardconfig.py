from subprocess import run, CompletedProcess
from pathlib import Path
from re import findall, match, RegexFlag, finditer
from json import dumps
from typing import TypedDict, NotRequired, Callable


UPSTREAM = "https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config.git";
DIR_XKEYBOARD_CONFIG = Path("xkeyboard-config")
DIR_XKEYBOARD_CONFIG_SYMBOLS = DIR_XKEYBOARD_CONFIG.joinpath("symbols/")
DIR_DATA = Path("data/")
#REGEX_SYMBOLS_ENTRY = r'(?P<default>default)?.*?$\n^xkb_symbols.*?"(?P<id>.*?)".*? *{$(?P<content>(\n|.)*?)^ *?};$'
REGEX_SYMBOLS_ENTRY = r'(?P<default>default)?.*?($\n^)?xkb_symbols.*?"(?P<id>.*?)".*?( |\n)*?{$(?P<content>(\n|.)*?)^ *?};$'
REGEX_SYMBOLS_ENTRY_ONE_LINE = r'(?P<default>default)?.*?($\n^)?xkb_symbols.*?"(?P<id>.*?)".*?{(?P<content>.*?) *?};$'
REGEX_ENTRY_INCLUDES = r'include "(?P<include>.*?)"'
REGEX_ENTRY_NAME = r'name\[Group\d*?\] *?= *?"(?P<name>.*?)";'
REGEX_ENTRY_KEYS = r'key <(?P<keycode>.*?)>\s*?{\s*?\[\s*?(?P<keys>.*?)\s*]'
REGEX_ENTRY_ID_FIND_LANGUAGE = r'^(.*?/)?(?P<language>[^\n\(]*)'

# These are not detected by the regex method, but instead manually added
AZERTY_STYLE_LAYOUTS = [
    # Non-alphabet characters
    "ara(azerty)",
    "ara(azerty_digits)",
    "sun_vndr/ara(azerty)",
    "sun_vndr/ara(azerty_digits)",
    "fr(geo)",
    "sun_vndr/fr(geo)",
    "ru(phonetic_azerty)",
    "gn",
    "gn(basic)",
    # Uses ara(azerty)
    "dz(ar)",
    "ma",
    "ma(arabic)",
]

AZERTY_DETECTORS = {
    "AD01": "a",
    "AD02": "z",
    #"AD03": "e"  TODO: needed?
}


def clone_or_pull_repo(repo: str=UPSTREAM, dirname: Path=DIR_XKEYBOARD_CONFIG) -> CompletedProcess[bytes]:
    if not dirname.exists():
        return run(["git", "clone", repo])
    else:
        return run(["git", "pull"], cwd=dirname)

def write_json(to_write: object, filename: str):
    _ = DIR_DATA.joinpath(f"{filename}.min.json").write_text(dumps(to_write))
    _ = DIR_DATA.joinpath(f"{filename}.json").write_text(dumps(to_write, indent=4))
            

# { layout_id: file_content  }
def fetch_individual_symbols(entries: dict[str, str], content: str, filename: Path) -> dict[str, str]:
    symbol_entries = list(finditer(REGEX_SYMBOLS_ENTRY, content, RegexFlag.MULTILINE)) \
        + list(finditer(REGEX_SYMBOLS_ENTRY_ONE_LINE, content, RegexFlag.MULTILINE))
    for symbol_entry in symbol_entries:
        entry_id = symbol_entry.group("id")
        is_default = symbol_entry.group("default") == "default"
        entry_content = symbol_entry.group("content")
        if is_default:
            print(f"Found default for {filename}, adding as {filename} & {filename}({entry_id})")
            entries[f"{filename}"] = entry_content
        entries[f"{filename}({entry_id})"] = entry_content
    return entries

def skip(id_str: str) -> bool:
    return id_str.startswith("kpdl") \
        or id_str.startswith("level")

def super_include(xkb_entries: dict[str, str], content: str, include_from: str):
    includes: list[str] = findall(REGEX_ENTRY_INCLUDES, content)
    #print(f"Includes for {symbol_id}: {includes}")
    for include in includes:
        # TODO: skip data that is currently not used & would require extra implementation
        if skip(include):
            print("Skipping keypad behaviour include")
            continue

        old_content = content
        print(f"Including {include} from {include_from}")
        content = old_content.replace(f'include "{include}"', super_include(xkb_entries, xkb_entries[include], include_from))
        if content != old_content:
            print("Succesful include!")
        else:
            raise Exception("Include failed")
    return content

class Keymap(TypedDict):
    name: NotRequired[str]
    id: str
    keys: NotRequired[dict[str, list[str]]]


class XkeyboardConfig(TypedDict):
    all: dict[str, Keymap]
    azerty: dict[str, Keymap]
    azerty_style: dict[str, Keymap]
    azerty_all: dict[str, Keymap]



def parseXkeyboardConfig(save: bool=True) -> XkeyboardConfig:
    """Step 0:
        - Clone xkeyboard-config if dir doesn't exist
        - Otherwise, pull changes from upstream
    """
    _ = clone_or_pull_repo()
    

    """Step 1:
        - Fetch all file contents
        - Parse individual symbols
        - Save individual symbols in xkb_entries dict
    """

    xkb_entries: dict[str, str] = dict()
    symbol_files = list(DIR_XKEYBOARD_CONFIG_SYMBOLS.glob("**"))
    for symbol_file in symbol_files:
        # Determine if file should be skipped
        filename = symbol_file.relative_to(DIR_XKEYBOARD_CONFIG_SYMBOLS)
        if symbol_file.is_dir() or skip(str(filename)):
            continue

        file_content = symbol_file.read_text("UTF-8")
        xkb_entries = fetch_individual_symbols(xkb_entries, file_content, filename)        

    out: XkeyboardConfig = {
        "all": dict(),
        "azerty": dict(),
        "azerty_style": dict(),
        "azerty_all": dict()
    }

    """Step 2:
        - Iterate over all symbol contents
        - Parse them into dicts()
    """
    for symbol_id in xkb_entries:
        # Include the includes. Minimize the maximize or whatever
        print("-----")
        print("Parsing " + symbol_id)
        symbol_content = xkb_entries[symbol_id]
        symbol_content_included = super_include(xkb_entries, symbol_content, symbol_id)

        entry: Keymap = {"id": symbol_id}

        entry_name = list(finditer(REGEX_ENTRY_NAME, symbol_content))
        print("\t> Fetching entry name")
        if entry_name:
            print("\tFound entry name")
            entry["name"] = entry_name[0].group("name")
        entry["keys"] = dict()
        print("> Fetching entry keys")
        entry_keys = list(finditer(REGEX_ENTRY_KEYS, symbol_content_included))

        for key_match in entry_keys:
            keys: list[str] = key_match.group("keys").replace(" ", "").replace("\t", "").split(",")
            if len(keys) < 1:
                raise IndexError("Keys too small")
            if keys[0] == "" and len(keys) == 1:
                continue
            entry["keys"][key_match.group("keycode")] = keys

        out["all"][symbol_id] = entry
        
        print("> Determining if Azerty")
        is_azerty = False
        for keycode in AZERTY_DETECTORS:
            try:
                keys = entry["keys"][keycode]
            except KeyError as e:
                print(f"\tCouldn't find keycode {e.args[0]}, not azerty")
                is_azerty = False
                break
            detector = AZERTY_DETECTORS[keycode]
            if detector.lower() in keys or detector.upper() in keys:
                print(f"\tFound {detector} in {keys}")
                is_azerty = True
            else:
                print(f"\tDidn't find {detector} in {keys}, not azerty")
                is_azerty = False
                break
        if is_azerty:
            print("Is Azerty!")
            out["azerty"][symbol_id] = entry
        elif symbol_id in AZERTY_STYLE_LAYOUTS:
            print(f"Hardcoded azerty style layout ({symbol_id})")
            out["azerty_style"][symbol_id] = entry
        elif "azerty" in symbol_content_included.lower():
            raise NotImplementedError(f"Azerty not detected, but 'azerty' was detected in symbol content ({symbol_id})")

    out["azerty_all"] = {**out["azerty"], **out["azerty_style"]}


    """Step 3:
        - Save processed data into json files
    """
    if save:
        for output in ["all", "azerty", "azerty-style", "azerty-all"]:
            data_key = output.replace("-", "_")
            if data_key not in out:
                raise Exception(f"{data_key} not in out: {out}")
            to_write: dict[str, Keymap] = out[data_key]
            write_json(to_write, output)
            
    return out

class NumericRowStyle(TypedDict):
    id: str  # for example, tg(basic)
    characters: list[str]  # for ['ampersand', 'U0301', 'U0300', 'parenleft' ]
    name: NotRequired[str]  # For example French (Togo)


type NumericRowStyles = dict[str, list[NumericRowStyle]]
def getNumericRowStyles(config: XkeyboardConfig, write:bool=True) -> NumericRowStyles:
    """Step 4:
        - Determine default numeric rows for all azerty keyboards
    """
    all_azerty = config["azerty_all"]

    azerty_numerics: dict[str, list[NumericRowStyle]] = dict()
    language_row_styles: dict[str, set[str]] = dict()
    for entry_id in all_azerty:
        entry = all_azerty[entry_id]
        print(f"Processing entry {entry['id']}")
        characters: list[str] = list()
        # get AE01-9 without modifiers, the numerical row

        for index in range(1, 10):
            assert "keys" in entry
            value: str = entry["keys"][f"AE{index:02}"][0]
            if type(value) == str:
                characters.append(value)

        out: NumericRowStyle = {
            "id": entry["id"],
            "characters": characters  # Used in niri
        }
        if "name" in entry:
            out["name"] = entry["name"]
        
        # Example: ampersand,eacute,quotedbl,apostrophe,parenleft,minus,egrave,underscore,ccedilla
        row_style = ",".join(out["characters"])

        if row_style not in azerty_numerics:
            azerty_numerics[row_style] = list()
        azerty_numerics[row_style].append(out)
        
        language = match(REGEX_ENTRY_ID_FIND_LANGUAGE, out["id"])
        if language:
            language = language.group("language")
        else:
            raise Exception("couldn't find language")
        
        if language not in language_row_styles.keys():
            language_row_styles[language] = set()
        language_row_styles[language].add(row_style)

    if write:
        azerty_numerics_write: dict[str,list[str]] = {}
        get_id: Callable[[NumericRowStyle], str] = lambda data: data["id"]
        for style in azerty_numerics:
            azerty_numerics_write[style] = list(map(get_id, azerty_numerics[style]))

        write_json(azerty_numerics_write, "azerty-numerics")

        language_row_styles_with_lists: dict[str, list[str]] = {}
        for language in language_row_styles:
            language_row_styles_with_lists[language] = list(language_row_styles[language])

        write_json(language_row_styles_with_lists, "azerty-row-styles")

    return azerty_numerics



