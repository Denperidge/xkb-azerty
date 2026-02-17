from os.path import dirname, exists
from subprocess import run
from glob import glob
from pathlib import Path
from re import findall

UPSTREAM = "https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config.git";
DIR_XKEYBOARD_CONFIG = Path("xkeyboard-config")

# These are not detected by the regex method, but instead manually added
AZERTY_STYLE_LAYOUTS = [
    "ara(azerty)"
]

AZERTY_DETECTORS = {
    "AD01": "a",
    "AD02": "z",
    "AD03": "e"
}

#AD01.*?(a|A)\,
#name\[Group\d*?\]=\"(?P<name>.*?)\"(\n|.)*?AD01.*?(a|A)\,(.|\n)*?^};$


def clone_or_pull_repo(repo=UPSTREAM, dirname=DIR_XKEYBOARD_CONFIG):
    if not dirname.exists():
        run(["git", "clone", repo])
    else:
        run(["git", "pull"], cwd=dirname)

if __name__ == "__main__":
    clone_or_pull_repo()

    #print(dirname(__file__))
    symbol_files = list(DIR_XKEYBOARD_CONFIG.glob("symbols/**"))
    for symbol_file in symbol_files:
        if symbol_file.is_dir():
            continue
        
        regex = "name\[Group\d*?\]=\"(?P<name>.*?)\"(\n|.)*?"
        for keycode in AZERTY_DETECTORS:
            expected = AZERTY_DETECTORS[keycode]
            regex += f".*?{keycode}.*?({expected.lower()}|{expected.upper()}),.*?\\n"
                
        content = symbol_file.read_text("UTF-8")
        matches = findall(regex, content)
        if len(matches) > 0:
            print(f"Detected Azerty: {matches[0][0]} (path: {symbol_file})")
            print("-----")
        elif "azerty" in content.lower():
            print(f"Didn't detect Azerty using regex, but the file contains the string 'azerty'. Is the Regex failing? (Path: {symbol_file})")
            print("-----")