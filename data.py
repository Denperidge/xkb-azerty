from os.path import dirname, exists
from subprocess import run

UPSTREAM = "https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config.git";
DIRNAME = "xkeyboard-config"

# These are not detected by the regex method, but instead manually added
AZERTY_STYLE_LAYOUTS = [
    "ara(azerty)"
]

AZERTY_DETECTORS = {
    "AD01": "a",
    "AD02": "z",
    "AD03": "e"
}

def clone_or_pull_repo(repo=UPSTREAM, dirname=DIRNAME):
    if not exists(dirname):
        run(["git", "clone", repo])
    else:
        run(["git", "pull"], cwd=dirname)

if __name__ == "__main__":
    clone_or_pull_repo()

    print(dirname(__file__))