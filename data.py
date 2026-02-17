from os.path import dirname, exists
from subprocess import run
from glob import glob
from pathlib import Path
from re import findall

UPSTREAM = "https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config.git";
DIR_XKEYBOARD_CONFIG = Path("xkeyboard-config")

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

def build_regex(detectors=AZERTY_DETECTORS):
    regex = r'name\[Group\d*?\]="(?P<name>.*?)"(\n|.)*?'
    for keycode in detectors:
        expected = detectors[keycode]
        regex += f".*?{keycode}.*?({expected.lower()}|{expected.upper()}),.*?\\n"
    return regex

if __name__ == "__main__":
    clone_or_pull_repo()
    regex = build_regex()

    symbol_files = list(DIR_XKEYBOARD_CONFIG.glob("symbols/**"))
    for symbol_file in symbol_files:
        # Determine if file should be skipped
        if symbol_file.is_dir():
            continue
        elif symbol_file.stem in AZERTY_STYLE_LAYOUTS:
            print(f"Skipping known exception {symbol_file.stem}")
            continue

        content = symbol_file.read_text("UTF-8")
        matches = findall(regex, content)
        if len(matches) > 0:
            print(f"Azerty detected in {symbol_file}:")
            for match in matches:
                print(f"\t- {match[0]}")
            print("-----")
        elif "azerty" in content.lower():
            print(f"Didn't detect Azerty using regex, but the file contains the string 'azerty'. Is the Regex failing? (Path: {symbol_file})")
            print("-----")