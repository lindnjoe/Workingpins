import pytest

import importlib
import sys
import types


class FakePins:
    class error(Exception):
        pass

    def __init__(self, printer):
        self.printer = printer
        self.chips = {}

    def register_chip(self, name, chip):
        self.chips[name] = chip

    def parse_pin(self, pin_desc, can_invert=False, can_pullup=False):
        if ':' not in pin_desc:
            raise self.error('invalid pin')
        chip, pin = pin_desc.split(':', 1)
        if chip not in self.chips:
            raise self.error("Unknown pin chip name '%s'" % chip)
        return {
            'chip_name': chip,
            'pin': pin,
            'invert': False,
            'pullup': False,
        }


class FakeGCode:
    def __init__(self):
        self.commands = {}
        self.responses = []

    def register_mux_command(self, name, group, cname, func, desc=None):
        self.commands[(name, cname)] = func

    def respond_info(self, msg):
        self.responses.append(msg)


class FakePrinter:
    def __init__(self):
        self.objects = {}
        self.objects["gcode"] = FakeGCode()
        PinsCls = FakePins
        mod = sys.modules.get("pins")
        if mod is not None and hasattr(mod, "Pins"):
            PinsCls = mod.Pins
        self.objects["pins"] = PinsCls(self)
        self.reactor = type("R", (), {"monotonic": lambda self: 0.0})()

    def lookup_object(self, name, default=None):
        return self.objects.get(name, default)

    def add_object(self, name, obj):
        self.objects[name] = obj

    def get_reactor(self):
        return self.reactor


class FakeConfig:
    def __init__(self, printer, name):
        self.printer = printer
        self._name = name

    def get_printer(self):
        return self.printer

    def get_name(self):
        return self._name

    def error(self, msg):
        raise Exception(msg)


class FakeGcmd:
    def __init__(self, params=None):
        self.params = params or {}
        self.responses = []

    def get_int(self, name, default=None):
        return int(self.params.get(name, default))

    def respond_info(self, msg):
        self.responses.append(msg)


@pytest.fixture
def printer():
    return FakePrinter()


@pytest.fixture
def ams(monkeypatch, printer):
    pins_mod = types.ModuleType("pins")

    class Pins(FakePins):
        pass

    pins_mod.Pins = Pins
    pins_mod.error = FakePins.error
    monkeypatch.setitem(sys.modules, "pins", pins_mod)

    # Replace printer pins with the patched class
    printer.objects["pins"] = pins_mod.Pins(printer)

    ams_pin = importlib.import_module("ams_pin")
    yield ams_pin
    monkeypatch.delitem(sys.modules, "ams_pin", raising=False)
    monkeypatch.delitem(sys.modules, "pins", raising=False)


@pytest.fixture
def chip(printer, ams):
    cfg = FakeConfig(printer, "ams_pin")
    return ams.load_config(cfg)


def test_prefix(printer, ams):
    cfg = FakeConfig(printer, "ams_pin pin2")
    pin = ams.load_config_prefix(cfg)
    assert pin.name == "pin2"


def test_watcher_and_gcode(printer, chip, ams):
    pin = chip.pins["pin1"]
    triggered = []
    pin.register_watcher(lambda v: triggered.append(v))
    gcode = printer.lookup_object("gcode")
    set_cmd = gcode.commands[("SET_AMS_PIN", "pin1")]
    query_cmd = gcode.commands[("QUERY_AMS_PIN", "pin1")]

    set_cmd(FakeGcmd({"VALUE": 1}))
    assert pin.state
    assert triggered == [False, True]

    gcmd = FakeGcmd()
    query_cmd(gcmd)
    assert "ams_pin pin1: 1" in gcmd.responses[0]


def test_auto_parse(printer, ams, monkeypatch):
    import importlib
    ams = importlib.reload(ams)
    printer.objects["pins"] = sys.modules["pins"].Pins(printer)
    ppins = printer.lookup_object("pins")
    res = ppins.parse_pin("ams_pin:pin3")
    assert res["chip_name"] == "ams_pin"
    assert res["pin"] == "pin3"
