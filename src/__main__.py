from .xkeyboardconfig import getNumericRowStyles, parseXkeyboardConfig
from .niri import generate_niri_md

xkbconfig = parseXkeyboardConfig()
numeric_row_styles = getNumericRowStyles(xkbconfig)

_ = generate_niri_md(numeric_row_styles)
