from os.path import dirname, exists
from subprocess import run
from glob import glob
from pathlib import Path
from re import findall, match, RegexFlag, finditer
from json import dumps

UPSTREAM = "https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config.git";
DIR_XKEYBOARD_CONFIG = Path("xkeyboard-config")
DIR_XKEYBOARD_CONFIG_SYMBOLS = DIR_XKEYBOARD_CONFIG.joinpath("symbols/")
DIR_DATA = Path("data/")
MARKDOWN_OUT = DIR_DATA.joinpath("numeric-row.md")
MARKDOWN_TEMPLATE = Path("template.md").read_text()

#REGEX_SYMBOLS_ENTRY = r'(?P<default>default)?.*?$\n^xkb_symbols.*?"(?P<id>.*?)".*? *{$(?P<content>(\n|.)*?)^ *?};$'
REGEX_SYMBOLS_ENTRY = r'(?P<default>default)?.*?($\n^)?xkb_symbols.*?"(?P<id>.*?)".*?( |\n)*?{$(?P<content>(\n|.)*?)^ *?};$'
REGEX_SYMBOLS_ENTRY_ONE_LINE = r'(?P<default>default)?.*?($\n^)?xkb_symbols.*?"(?P<id>.*?)".*?{(?P<content>.*?) *?};$'
REGEX_ENTRY_INCLUDES = r'include "(?P<include>.*?)"'
REGEX_ENTRY_NAME = r'name\[Group\d*?\] *?= *?"(?P<name>.*?)";'
REGEX_ENTRY_KEYS = r'key <(?P<keycode>.*?)>\s*?{\s*?\[\s*?(?P<keys>.*?)\s*]'

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

MARKDOWN_PREFIX = """### AZERTY
When using Niri with an AZERTY keyboard layout, the default workspace keybinds (or any keybinds using numbers) will not work as intended.
"""


def clone_or_pull_repo(repo=UPSTREAM, dirname=DIR_XKEYBOARD_CONFIG):
    if not dirname.exists():
        run(["git", "clone", repo])
    else:
        run(["git", "pull"], cwd=dirname)

def fetch_individual_symbols(entries, content, filename):
    symbol_entries = list(finditer(REGEX_SYMBOLS_ENTRY, file_content, RegexFlag.MULTILINE)) \
        + list(finditer(REGEX_SYMBOLS_ENTRY_ONE_LINE, file_content, RegexFlag.MULTILINE))
    for symbol_entry in symbol_entries:
        entry_id = symbol_entry.group("id")
        is_default = symbol_entry.group("default") == "default"
        entry_content = symbol_entry.group("content")
        if is_default:
            print(f"Found default for {filename}, adding as {filename} & {filename}({entry_id})")
            entries[f"{filename}"] = entry_content
        entries[f"{filename}({entry_id})"] = entry_content
    return entries

def skip(id_str):
    return id_str.startswith("kpdl") \
        or id_str.startswith("level")

def super_include(content, include_from):
    includes = findall(REGEX_ENTRY_INCLUDES, content)
    print(f"Includes for {symbol_id}: {includes}")
    for include in includes:
        # TODO: skip data that is currently not used & would require extra implementation
        if skip(include):
            print("Skipping keypad behaviour include")
            continue

        old_content = content
        print(f"Including {include} from {include_from}")
        content = old_content.replace(f'include "{include}"', super_include(xkb_entries[include], include_from))
        if content != old_content:
            print("Succesful include!")
        else:
            raise Error("Include failed")
    return content

if __name__ == "__main__":
    """Step 0:
        - Clone xkeyboard-config if dir doesn't exist
        - Otherwise, pull changes from upstream
    """
    clone_or_pull_repo()
    
    """Step 1:
        - Fetch all file contents
        - Parse individual symbols
        - Save individual symbols in xkb_entries dict
    """
    xkb_entries = dict()
    symbol_files = list(DIR_XKEYBOARD_CONFIG_SYMBOLS.glob("**"))
    for symbol_file in symbol_files:
        # Determine if file should be skipped
        filename = symbol_file.relative_to(DIR_XKEYBOARD_CONFIG_SYMBOLS)
        if symbol_file.is_dir() or skip(str(filename)):
            continue

        file_content = symbol_file.read_text("UTF-8")
        xkb_entries = fetch_individual_symbols(xkb_entries, file_content, filename)        

    processed_all = dict()
    processed_azerty = dict()
    processed_azerty_style = dict()

    """Step 2:
        - Iterate over all symbol contents
        - Parse them into dicts()
    """
    for symbol_id in xkb_entries:
        # Include the includes. Minimize the maximize or whatever
        print("-----")
        print("Parsing " + symbol_id)
        symbol_content = xkb_entries[symbol_id]
        symbol_content_included = super_include(symbol_content, symbol_id)

        entry = {"id": symbol_id}

        entry_name = list(finditer(REGEX_ENTRY_NAME, symbol_content))
        print("\t> Fetching entry name")
        if entry_name:
            print("\tFound entry name")
            entry["name"] = entry_name[0].group("name")
        print("> Fetching entry keys")
        entry_keys = list(finditer(REGEX_ENTRY_KEYS, symbol_content_included))
        entry["keys"] = dict()

        for key_match in entry_keys:
            keys = key_match.group("keys").replace(" ", "").replace("\t", "").split(",")
            if len(keys) < 1:
                raise IndexError("Keys too small")
            if keys[0] == "" and len(keys) == 1:
                continue
            entry["keys"][key_match.group("keycode")] = keys

        processed_all[symbol_id] = entry
        
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
            processed_azerty[symbol_id] = entry
        elif symbol_id in AZERTY_STYLE_LAYOUTS:
            print(f"Hardcoded azerty style layout ({symbol_id})")
            processed_azerty_style[symbol_id] = entry
        elif "azerty" in symbol_content_included.lower():
            raise NotImplementedError(f"Azerty not detected, but 'azerty' was detected in symbol content ({symbol_id})")

    """Step 3:
        - Save processed data into json files
    """
    for output in [
        ["all", processed_all],
        ["azerty", processed_azerty],
        ["azerty-style", processed_azerty_style]
    ]:
        DIR_DATA.joinpath(f"{output[0]}.min.json").write_text(dumps(output[1]))
        DIR_DATA.joinpath(f"{output[0]}.json").write_text(dumps(output[1], indent=4))
    

    """Step 4:
        - Determine default numeric rows for azerty keyboards
        - Save the result to markdown files
    """
    all_azerty = {**processed_azerty, **processed_azerty_style}
    azerty_numerics = dict()
    for entry_id in all_azerty:
        entry = all_azerty[entry_id]
        print(f"Processing entry {entry['id']}")
        characters = list()
        # get AE01-9
        for index in range(1, 10):
            characters.append(entry["keys"][f"AE{index:02}"][0])

        out = {
            "id": entry["id"],
            "characters": characters
        }
        if "name" in entry:
            out["name"] = entry["name"]
        
        row_style = ",".join(out["characters"])

        if row_style not in azerty_numerics:
            azerty_numerics[row_style] = list()
        azerty_numerics[row_style].append(out)
    
    markdown_output = MARKDOWN_PREFIX
    for row_style in azerty_numerics:
        row_style_entries = azerty_numerics[row_style]
        out = MARKDOWN_TEMPLATE

        characters = row_style_entries[0]["characters"]
        index = 0
        for character in characters:
            out = out.replace("{" + str(index+1) + "}", character)
            index+=1

        layouts = ""
        first = True
        for entry in row_style_entries:
            if first:
                first = False
            else:
                layouts += ", "
            layouts += entry["id"]
            if "name" in entry:
                layouts += f" [{entry['name']}]"
        out = out.replace("{layouts}", layouts)

        markdown_output += out

    MARKDOWN_OUT.write_text(markdown_output)
  