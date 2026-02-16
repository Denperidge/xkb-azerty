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
        
        regex = ""
        for keycode in AZERTY_DETECTORS:
            expected = AZERTY_DETECTORS[keycode]
            regex += f".*?{keycode}.*?({expected.lower()}|{expected.upper()})\,.*?\\n"
        
        #findall()
        
        content = symbol_file.read_text("UTF-8")
        #print(content)