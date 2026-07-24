from urllib.request import urlretrieve
from os.path import dirname, join

def fetch_reqs():
    _ = urlretrieve(url="https://raw.githubusercontent.com/sxyazi/yazi/refs/tags/shipped/yazi-config/preset/keymap-default.toml",
        filename=join(dirname(__file__), "../vendor/yazi-keymap-default.toml"))
