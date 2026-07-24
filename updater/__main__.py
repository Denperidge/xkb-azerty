from .xkeyboardconfig import getNumericRowStyles, parseXkeyboardConfig
from .niri import generate_niri_md
from .vendor import fetch_reqs
from .libxkbcommon import xkb_alias_to_character

xkbconfig = parseXkeyboardConfig()
numeric_row_styles = getNumericRowStyles(xkbconfig)

# data/numeric-row.md
_ = generate_niri_md(numeric_row_styles)



# vendor/defaults
_ = fetch_reqs()  # For webtool

