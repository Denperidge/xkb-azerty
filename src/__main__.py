from .xkeyboardconfig import getNumericRowStyles, parseXkeyboardConfig
from .niri import generate_niri_md
from .vendor import fetch_reqs

xkbconfig = parseXkeyboardConfig()
numeric_row_styles = getNumericRowStyles(xkbconfig)

_ = generate_niri_md(numeric_row_styles)
_ = fetch_reqs()  # For webtool
