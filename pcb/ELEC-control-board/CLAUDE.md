# ELEC-control-board (KiCad 10)

Read `SPEC.md` in this folder before any change. It is the source of truth for parts, values and nets.

- Kevin places symbols and draws wires in KiCad. Claude checks and fixes: values, net labels, no-connects, fields, connectivity. Don't add symbols or route wires by editing the file unless Kevin asks.
- Before editing `*.kicad_sch`, confirm KiCad has the schematic closed (KiCad does not reload; saving there overwrites your edit).
- After every edit: run ERC (command in SPEC.md), report errors by reference and pin, export the netlist and run `tools/check_netlist.py` against SPEC.md, and run PCB DRC (`0` errors, `0` unconnected, `0` schematic parity).
- Never connect J5/J6 pin 4 to +5V or ESP_5V.
- Never power J8 (HX711 brake) from +5V — must stay on +3V3 (5 V DOUT damages ESP32; 3.3 V SCK is out-of-spec for 5 V HX711).
- Never put +5V, ESP_5V, or +3V3 on J13 (LED_DATA) — addressable LED strips must use a separate fused buck converter.
- Commit with a short message after each finished block; push only when Kevin says.
