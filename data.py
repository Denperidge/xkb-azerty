from os.path import dirname, exists
from subprocess import run
from glob import glob
from pathlib import Path
from re import findall, match, RegexFlag, finditer

UPSTREAM = "https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config.git";
DIR_XKEYBOARD_CONFIG = Path("xkeyboard-config")
DIR_XKEYBOARD_CONFIG_SYMBOLS = DIR_XKEYBOARD_CONFIG.joinpath("symbols/")

#REGEX_SYMBOLS_ENTRY = r'(?P<default>default)?.*?$\n^xkb_symbols.*?"(?P<id>.*?)".*? *{$(?P<content>(\n|.)*?)^ *?};$'
REGEX_SYMBOLS_ENTRY = r'(?P<default>default)?.*?($\n^)?xkb_symbols.*?"(?P<id>.*?)".*?( |\n)*?{$(?P<content>(\n|.)*?)^ *?};$'
REGEX_SYMBOLS_ENTRY_ONE_LINE = r'(?P<default>default)?.*?($\n^)?xkb_symbols.*?"(?P<id>.*?)".*?{(?P<content>.*?) *?};$'
REGEX_INCLUDES = r'include "(?P<include>.*?)"'

# These are not detected by the regex method, but instead manually added
AZERTY_STYLE_LAYOUTS = [
    "ara"  # ara(azerty) & ara(azerty_digits)
]


AZERTY_DETECTORS = {
    "AD01": "a",
    "AD02": "z",
    "AD03": "e"
}

#name\[Group\d*?\]=\"(?P<name>.*?)\"(\n|.)*?AD01.*?(a|A)\,(.|\n)*?^};$


def clone_or_pull_repo(repo=UPSTREAM, dirname=DIR_XKEYBOARD_CONFIG):
    if not dirname.exists():
        run(["git", "clone", repo])
    else:
        run(["git", "pull"], cwd=dirname)

def fetch_individual_symbols(content, filename):
    global xkb_entries
    symbol_entries = list(finditer(REGEX_SYMBOLS_ENTRY, file_content, RegexFlag.MULTILINE)) \
        + list(finditer(REGEX_SYMBOLS_ENTRY_ONE_LINE, file_content, RegexFlag.MULTILINE))
    for symbol_entry in symbol_entries:
        entry_id = symbol_entry.group("id")
        is_default = symbol_entry.group("default") == "default"
        entry_content = symbol_entry.group("content")
        if is_default:
            print(f"Found default for {filename}, adding as {filename} & {filename}({entry_id})")
            xkb_entries[f"{filename}"] = entry_content
        xkb_entries[f"{filename}({entry_id})"] = entry_content

def build_regex(detectors=AZERTY_DETECTORS):
    regex = r'name\[Group\d*?\]="(?P<name>.*?)"(\n|.)*?'
    for keycode in detectors:
        expected = detectors[keycode]
        regex += f".*?{keycode}.*?({expected.lower()}|{expected.upper()}),.*?\\n"
    print(f"Final regex: {regex}")
    return regex

def super_include(content, include_from):
    includes = findall(REGEX_INCLUDES, content)
    print(f"Includes for {symbol_id}: {includes}")
    for include in includes:
        # TODO: skip data that is currently not used & would require extra implementation
        if include.startswith("kpdl") or include.startswith("level"):
            print("Skipping keypad behaviour include")
            continue

        print(f"Including {include} from {include_from}")
        new_content = content.replace(f'include "{include}"', super_include(xkb_entries[include], include_from))
        if content != new_content:
            print("Succesful include!")
        else: 
            raise Error("Include failed")
    

    return content
    


if __name__ == "__main__":
    clone_or_pull_repo()
    regex = build_regex()



    xkb_entries = dict()
    symbol_files = list(DIR_XKEYBOARD_CONFIG_SYMBOLS.glob("**"))
    for symbol_file in symbol_files:
        # Determine if file should be skipped
        filename = symbol_file.relative_to(DIR_XKEYBOARD_CONFIG_SYMBOLS)
        if symbol_file.is_dir():
            continue
        #elif filename in AZERTY_STYLE_LAYOUTS:
        #    print(f"Skipping known exception {filename}")
        #    continue
        #xkb_entries[filename] = dict()

        file_content = symbol_file.read_text("UTF-8")
        fetch_individual_symbols(file_content, filename)        

    """
    We're considering 3 levels of load importance for xkb entries
        1. Highest priority; commonly imported symbols, like latin (found in latin(basic)). These are manually figured out
        2. Middle priority; symbols that don't include imports from within the same file
        3. Lowest priority; symbols that include imports from within the same file
    """

    processed_xkb_entries = dict()
    """
    for filename in [
        "latin",
        "us"
    ]:
        pass
    """
    
    # Iterate over all symbol contents
    for symbol_id in xkb_entries:
        # Include the includes. Minimize the maximize or whatever
        symbol_content = super_include(xkb_entries[symbol_id], symbol_id)
        print("---")


    """
            matches = findall(regex, entry_content)
            if len(matches) > 0:
                print(f"Azerty detected in {symbol_file}:")
                for match in matches:
                    print(f"\t- {match[0]}")
                print("-----")
            elif "azerty" in entry_content.lower():
                print(f"Didn't detect Azerty using regex, but {entry_id} contains the string 'azerty'. Is the Regex failing? (Path: {symbol_file})")
                print("-----")
        """