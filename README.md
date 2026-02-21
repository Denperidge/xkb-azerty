# xkb-azerty
There are shockingly little resources about Azerty layouts out there, which sucks when you're a developer/linux user using Azerty.

This project was part of the research needed for my documentation of [configuring Azerty for Niri](https://github.com/YaLTeR/niri/pull/3387), which uses xkeyboard-config/xkb for keyboard layout selection.

The scripts in this repository do *not* rely on an existing X11 installation; instead, it parses the upstream xkeyboard-config repository for the individual keyboard layouts.

## Explanation
### View output data
Simply see the [data/](data/) folder for the latest exported data! To run the script yourself/update the data in directory, [see below](#run-scriptsrefresh-data).

### Azerty-style layouts
These keyboard layouts are Azerty style: while they don't have the azerty letter keys, they still have other azerty features (e.g. the numeric row).

### Pivotal keycodes
- AD01-AD06: the QWERTY or AZERTY letter keys. Due to qwerty being the default, only AD01-02 (A & Z) are needed to identify Azerty.
- AE01-AE12: the numerical keys/top row, usually including numbers 0-9 and symbols. These are variable between azerty layouts, but very relevant for xkb shortcut binding etc. For the purposes of the [Niri data export](data/numeric-row.md), AE01-AE09 (0-9) are considered.

## How-to
### Run scripts/refresh data
Requirements: `python3`, `git`

```sh
git clone https://github.com/Denperidge/xkb-azerty.git
cd xkb-azerty/

python data.py  # Depending on your OS/configuration, python3 or py -3 must be used

# Done!
```

## License
This project and the generated info therein are released into the public domain through [the Unlicense](LICENSE).
