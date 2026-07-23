from pathlib import Path
from .xkeyboardconfig import NumericRowStyles

DIR_DATA = Path("data/")

MARKDOWN_OUT = DIR_DATA.joinpath("numeric-row.md")
MARKDOWN_TEMPLATE = Path("template.md").read_text()
MARKDOWN_PREFIX = """### AZERTY
When using Niri with an AZERTY keyboard layout, the default workspace keybinds (or any keybinds using numbers) will not work as intended.

"""

def generate_niri_md(azerty_numerics: NumericRowStyles):
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

    _ = MARKDOWN_OUT.write_text(markdown_output)
  
