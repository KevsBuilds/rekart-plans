#!/usr/bin/env python3
"""Compare the ELEC-control-board netlist against SPEC.md (sheets 1 and 2).

Usage: tools/check_netlist.py [netlist.net] [SPEC.md]
Defaults: pcb/ELEC-control-board/reports/netlist.net (written by pcb/check.sh)
          pcb/ELEC-control-board/SPEC.md
Exit 0 = every check passed, 1 = any failure, 2 = could not read input.

EXPECTED below is SPEC.md's "Nets" and "Nets (sheet 2)" sections written out pin by pin. ESP32
socket pins (J1/J2) come from the Freenove pin map on the sheet (verified by
Kevin against the USB-C board silkscreen, 2026-11-21).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOARD = ROOT / "pcb" / "ELEC-control-board"

# ---- ESP32 socket pins in use (pin map verified 2026-11-21, see sheet text box) ----
ESP32_PINS = {
    "+3V3": ["J1.1", "J1.16", "J1.17", "J1.18"],      # 3V3 pins
    "ESP_5V": ["J1.19", "J1.20"],                     # 5V pins
    "GND": ["J1.14", "J2.1", "J2.7", "J2.11", "J2.12", "J2.17", "J2.18", "J2.19", "J2.20"],
    "VBAT_SENSE": ["J1.3"],                           # GPIO36 (VP)
    "BUS_RX": ["J1.10"],                              # GPIO26
    "BUS_TX": ["J1.11"],                              # GPIO27
    # sheet 2
    "MODE": ["J1.4"],                                 # GPIO39 (VN)
    "ESTOP": ["J1.5"],                                # GPIO34
    "TF_RX_IO": ["J1.6"],                             # GPIO35 (not 39: erratum)
    "THR_ADC": ["J1.7"],                              # GPIO32
    "BRK_ADC": ["J1.8"],                              # GPIO33
    "SD_CS": ["J1.9"],                                # GPIO25
    "DIR_IO": ["J1.12"],                              # GPIO14
    "LCD_BL_IO": ["J1.15"],                           # GPIO13
    "SPI_MOSI": ["J2.2"],                             # GPIO23
    "I2C_SCL": ["J2.3"],                              # GPIO22
    "I2C_SDA": ["J2.6"],                              # GPIO21
    "SPI_MISO": ["J2.8"],                             # GPIO19
    "SPI_SCK": ["J2.9"],                              # GPIO18
    "LCD_CS": ["J2.10"],                              # GPIO5
    "LCD_DC": ["J2.13"],                              # GPIO4
}
# ESP32 pins that must stay unconnected (EN never goes to the screen: SPEC sheet 2)
ESP32_NC = ["J1.2", "J1.13", "J2.4", "J2.5", "J2.14", "J2.15", "J2.16"]

# ---- SPEC.md "Nets", pin by pin ----
# Diodes: pin 1 = K, pin 2 = A. C_Polarized: pin 1 = +.
EXPECTED = {
    # Power
    "+BATT": ["D2.1", "C1.1", "J4.1", "R1.1"],   # D2 K, C1 +, buck VIN+, divider top
    "GND": ["J3.2", "C1.2", "J4.2", "J4.4", "C2.2", "R2.2", "C3.2", "J5.1", "J6.1"],
    "+5V": ["J4.3", "C2.1", "JP1.1"],
    "ESP_5V": ["JP1.2"],
    # Battery sense
    "VBAT_SENSE": ["R1.2", "R2.1", "C3.1"],
    # Hoverboard bus
    "BUS_TX": ["R3.1"],
    "HB_PA3": ["R3.2", "J5.3", "J6.3"],
    "BUS_RX": ["J5.2", "D1.2", "R4.2"],
    "S_PA2": ["D1.1", "J6.2"],
    "+3V3": ["R4.1"],
    "HB_5V": ["J5.4", "J6.4"],
    # ---- sheet 2 ----
    # Pedals: divider 10k/12k, 100n
    "THR_SIG": ["J7.3", "R5.1"],
    "THR_ADC": ["R5.2", "R6.1", "C4.1"],
    "BRK_SIG": ["J8.3", "R7.1"],
    "BRK_ADC": ["R7.2", "R8.1", "C5.1"],
    # Steering
    "I2C_PU": ["JP2.2", "R9.1", "R10.1"],
    "I2C_SDA": ["J9.3", "R9.2"],
    "I2C_SCL": ["J9.4", "R10.2"],
    # Screen
    "LCD_VCC": ["JP3.2", "J10.1"],
    "LCD_CS": ["J10.3", "R11.2"],
    "LCD_RST": ["J10.4", "R18.2", "C9.1"],
    "LCD_DC": ["J10.5"],
    "SPI_MOSI": ["J10.6"],
    "SPI_SCK": ["J10.7"],
    "LCD_BL": ["J10.8", "R12.2"],
    "LCD_BL_IO": ["R12.1"],
    "SPI_MISO": ["J10.9"],
    "SD_CS": ["J10.10"],
    # Wheel controls
    "ESTOP": ["J11.1", "R13.2", "C6.1"],
    "MODE": ["J11.2", "R14.2", "C7.1"],
    "DIR": ["J11.3", "R15.2", "C8.1", "R16.1"],
    "DIR_IO": ["R16.2"],
    # TF-Luna
    "TF_TX": ["J12.3", "R17.1"],
    "TF_RX_IO": ["R17.2"],
}
EXPECTED["+5V"] += ["J7.1", "J8.1", "J12.1", "JP3.3"]
EXPECTED["+3V3"] += ["J9.1", "JP2.1", "JP3.1", "R11.1", "R18.1", "R13.1", "R14.1", "R15.1"]
EXPECTED["GND"] += ["J7.2", "J8.2", "R6.2", "C4.2", "R8.2", "C5.2", "J9.2", "J10.2", "C9.2",
                    "J11.4", "J11.5", "C6.2", "C7.2", "C8.2", "J12.2"]
NC_PINS = ESP32_NC + ["J11.6", "J12.4"]
for net, pins in ESP32_PINS.items():
    EXPECTED[net] = EXPECTED[net] + pins

# Unnamed nets in the series chain J3.1 -> F1 -> D2 (A->K) -> +BATT
UNNAMED = [{"J3.1", "F1.1"}, {"F1.2", "D2.2"}]


def parse(text):
    tok = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
    stack = [[]]
    for m in tok.finditer(text):
        t = m.group(0)
        if t == "(":
            stack.append([])
        elif t == ")":
            x = stack.pop()
            stack[-1].append(x)
        else:
            stack[-1].append(t[1:-1] if t.startswith('"') else t)
    return stack[0][0]


def kids(x, key):
    return [c for c in x if isinstance(c, list) and c and c[0] == key]


def val(x, key):
    k = kids(x, key)
    return k[0][1] if k and len(k[0]) > 1 else None


def spec_parts(spec_text):
    """Ref -> (lib symbol, value) from SPEC.md's Parts table."""
    parts = {}
    for line in spec_text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 3 or not re.match(r"^[A-Z]+\d", cells[0]):
            continue
        refs = [r.strip() for r in cells[0].split(",")]
        value = re.sub(r"\(.*?\)", "", cells[2]).replace("*", "").strip()
        values = [v.strip() for v in value.split(",")] if len(refs) > 1 else [value]
        for r, v in zip(refs, values):
            parts[r] = (cells[1], v)
    return parts


def main():
    net_path = Path(sys.argv[1]) if len(sys.argv) > 1 else BOARD / "reports" / "netlist.net"
    spec_path = Path(sys.argv[2]) if len(sys.argv) > 2 else BOARD / "SPEC.md"
    try:
        tree = parse(net_path.read_text())
        spec = spec_path.read_text()
    except OSError as e:
        print(f"check_netlist: {e}", file=sys.stderr)
        return 2

    fails = []
    def check(ok, msg):
        print(("PASS " if ok else "FAIL ") + msg)
        if not ok:
            fails.append(msg)

    # Components: refs, symbols, values vs SPEC Parts table
    comps = {}
    for c in kids(kids(tree, "components")[0], "comp"):
        ls = kids(c, "libsource")[0]
        comps[val(c, "ref")] = (f"{val(ls, 'lib')}:{val(ls, 'part')}", val(c, "value"))
    parts = spec_parts(spec.split("## Parts", 1)[1].split("## Nets", 1)[0])
    parts.update(spec_parts(spec.split("### Parts (sheet 2)", 1)[1].split("### Nets (sheet 2)", 1)[0]))
    check(set(comps) == set(parts),
          f"component refs match SPEC Parts (extra {sorted(set(comps) - set(parts))}, missing {sorted(set(parts) - set(comps))})")
    for ref in sorted(set(comps) & set(parts)):
        check(comps[ref] == parts[ref], f"{ref} symbol/value {comps[ref]} == SPEC {parts[ref]}")

    # Nets
    nets = {}
    for n in kids(kids(tree, "nets")[0], "net"):
        pins = {f"{val(nd, 'ref')}.{val(nd, 'pin')}" for nd in kids(n, "node")}
        pins = {p for p in pins if not p.startswith("#")}       # power symbols / flags
        name = val(n, "name")
        nets[name.rsplit("/", 1)[-1] if name.startswith("/") else name] = pins   # local labels: "/<sheet path>/NAME"

    section = spec.split("## Nets", 1)[-1].split("## Open questions", 1)[0]   # includes the sheet 2 section
    for name, want in EXPECTED.items():
        check(name in section, f"net name {name} appears in SPEC.md Nets section")
        got = nets.get(name, set())
        want = set(want)
        check(got == want, f"{name}: missing {sorted(want - got)}, extra {sorted(got - want)}")

    by_pins = {frozenset(p): name for name, p in nets.items()}
    for chain in UNNAMED:
        check(frozenset(chain) in by_pins, f"series net {sorted(chain)} exists alone (got {by_pins.get(frozenset(chain))})")

    # Every other pin must be alone on an unconnected net (no-connect)
    used = set().union(*EXPECTED.values(), *UNNAMED)
    for name, pins in nets.items():
        if name in EXPECTED or frozenset(pins) in [frozenset(c) for c in UNNAMED]:
            continue
        check(len(pins) <= 1 and not (pins & used), f"stray net {name}: {sorted(pins)}")
    all_pins = set().union(*nets.values())
    for ref in ("J1", "J2"):
        for i in range(1, 21):
            check(f"{ref}.{i}" in all_pins, f"{ref}.{i} present in netlist")

    # Explicit safety assertions
    hb = nets.get("HB_5V", set())
    check(hb == {"J5.4", "J6.4"}, "HB_5V touches only J5.4 and J6.4")
    for other in ("+5V", "ESP_5V", "+3V3"):
        check(not (hb & nets.get(other, set())), f"HB_5V not joined to {other}")
    check(not ({"J5.4", "J6.4"} & set().union(*(nets.get(k, set()) for k in ("+5V", "ESP_5V", "+3V3")))),
          "J5.4/J6.4 not on +5V/ESP_5V/+3V3")
    check("D1.1" in nets.get("S_PA2", set()), "D1 pin 1 (K) on S_PA2")
    check(any(p == {"D2.2", "F1.2"} for p in nets.values()),
          "D2 anode (pin 2) on the J3/F1 side")
    check("D2.1" in nets.get("+BATT", set()), "D2 cathode (pin 1) on +BATT")
    r4 = {n for n, p in nets.items() if p & {"R4.1", "R4.2"}}
    check(r4 == {"BUS_RX", "+3V3"}, f"R4 between BUS_RX and +3V3 (got {sorted(r4)})")
    r3 = {n for n, p in nets.items() if p & {"R3.1", "R3.2"}}
    check(r3 == {"BUS_TX", "HB_PA3"}, f"R3 between BUS_TX and HB_PA3 (got {sorted(r3)})")

    # No-connect pins: each alone on its own net
    for pin in NC_PINS:
        on = [nm for nm, p in nets.items() if pin in p]
        check(len(on) == 1 and nets[on[0]] == {pin}, f"{pin} is a no-connect (alone)")

    # Sheet 2 safety assertions
    def between(ref, a, b):
        got = {nm for nm, p in nets.items() if p & {f"{ref}.1", f"{ref}.2"}}
        check(got == {a, b}, f"{ref} between {a} and {b} (got {sorted(got)})")
    between("R5", "THR_SIG", "THR_ADC"); between("R6", "THR_ADC", "GND")
    between("R7", "BRK_SIG", "BRK_ADC"); between("R8", "BRK_ADC", "GND")
    between("R13", "ESTOP", "+3V3")        # E-stop NC to GND: open (pressed / cut) reads HIGH
    between("R16", "DIR", "DIR_IO")
    between("R17", "TF_TX", "TF_RX_IO")
    check("J1.6" in nets.get("TF_RX_IO", set()) and "J1.4" not in nets.get("TF_RX_IO", set()),
          "TF-Luna RX on GPIO35 (J1.6), not GPIO39 (J1.4)")
    check(not any(p.startswith(("J1.", "J2.")) for p in nets.get("LCD_RST", set())),
          "LCD_RST touches no ESP32 pin (not EN)")

    print()
    print(f"{len(fails)} failure(s)" if fails else "ALL CHECKS PASSED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
