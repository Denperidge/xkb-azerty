# xkb-azerty
There are shockingly little resources about Azerty layouts out there, which sucks when you're a developer/linux user using Azerty.

Part of the research needed for my documentation of [configuring Azerty for Niri](https://github.com/YaLTeR/niri/pull/3387), which uses xkeyboard-config/xkb for keyboard layout selection.

The scripts in this repository do *not* rely on an existing X11 installation; instead, it parses the upstream xkeyboard-config repository for the info.

## Reference
### Azerty layouts
### Azerty-style layouts
These keyboard layouts are Azerty style: while they don't have the azerty letter keys, they still have other azerty stylings

## Explanation
### Pivotal keycodes
- AD01-AD06: the QWERTY or AZERTY letter keys. Due to qwerty being the default, only AD01-03 are needed to identify azerty
- AE01-AE12: the numerical keys/top row, usually including numbers 0-9 and symbols. These are variable between azerty layouts, but very relevant for xkb shortcut binding etc.

## How-to

### Run scripts/refresh data
Requirements: python3

## x11/xkb/xkeyboard azerty profiles
Sourced from [Arch manual](https://man.archlinux.org/man/xkeyboard-config-2.7.en)
- Arabic: ara(azerty) + ara(azerty_digits)

