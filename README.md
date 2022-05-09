# THIS IS THE MAC VERSION OF QMK-DOVES

TODO: Remove the functionality instead of just commenting it out :)

A Python App to control functions used on my keyboard.

Works with this [keymap](https://github.com/kevinpanaro/qmk_firmware/tree/develop/keyboards/sofle/keymaps/kevinpanaro).

Needs a `config.ini` file at root level to find your device. Example:

```ini
[DEVICE]
; these need to be updated for every keyboard
VID=0xFC32
PID=0x0287
USAGE_PAGE=0xFF60
USAGE=0x61
RAW_EPSIZE=32
COLUMNS=5
ROWS=16
```
