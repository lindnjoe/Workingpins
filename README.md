# Workingpins

This repo provides a simple virtual input pin implementation for Klipper.
Eight global pins named `pin1` through `pin8` are available via the
`ams_pin:` prefix and may be referenced anywhere an endstop-style input pin
is expected.  A dedicated configuration section is optional, however the
`[ams_pin]` section **must appear before any reference** to the `ams_pin:`
pins so that Klipper can register the chip before parsing other modules.

Klipper processes configuration sections in order. The `[ams_pin]`
section should therefore be placed *before* any other section (or
included file) that references the `ams_pin:` prefix. The pins are
created automatically the first time the prefix is encountered, but
placing the section first avoids "Unknown pin chip name" errors.  An
example configuration referencing `pin1` via the provided virtual
filament sensor module is:

```ini
[ams_pin]        # optional
[virtual_filament_sensor my_sensor]
pin: ams_pin:pin1
```

Individual pin sections are optional – the pins exist globally once the
`ams_pin` module is imported.

If Klipper reports `Unknown pin chip name 'ams_pin'` during startup it
usually means the module was not copied into Klipper's
`klippy/extras/` directory.  Verify that `ams_pin.py` is located in that
directory and restart Klipper.

If you have existing scripts that import `virtual_input_pin.py` you can copy
that file as well; it simply re-exports everything from `ams_pin.py`.  Only the
`ams_pin.py` file is required for the prefix to be recognized.
