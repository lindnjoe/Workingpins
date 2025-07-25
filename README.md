# Workingpins

This repo provides a simple virtual input pin implementation for Klipper.
Eight global pins named `pin1` through `pin8` are available via the
`ams_pin:` prefix and may be referenced anywhere an endstop-style input pin
is expected.

Klipper processes configuration sections in order. A single
`[ams_pin]` section **must** appear *before* any other section that
uses the `ams_pin:` prefix so the chip is registered when other
modules parse their pins. The minimal configuration is:

```ini
[ams_pin]
```

Individual pin sections are optional – the pins exist globally once the
`[ams_pin]` section is processed.

Example usage with the provided virtual filament sensor module:

```ini
[ams_pin]

[virtual_filament_sensor my_sensor]
pin: ams_pin:pin1
```

If Klipper reports `Unknown pin chip name 'ams_pin'` during startup, ensure
that the `[ams_pin]` section appears before any other section that uses the
`ams_pin:` prefix.

Ensure `ams_pin.py` is located in Klipper's `klippy/extras/` directory so the `[ams_pin]` section loads correctly.
