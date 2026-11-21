# ELEC-control-board (KiCad 10)

Read `SPEC.md` in this folder before any change. It is the source of truth for parts, values and nets.

- Kevin places symbols and draws wires in KiCad. Claude checks and fixes: values, net labels, no-connects, fields, connectivity. Don't add symbols or route wires by editing the file unless Kevin asks.
- Before editing `*.kicad_sch`, confirm KiCad has the schematic closed (KiCad does not reload; saving there overwrites your edit).
- After every edit: run ERC (command in SPEC.md), report errors by reference and pin, then export the netlist and compare it to SPEC.md's Nets section.
- Never connect J5/J6 pin 4 to +5V or ESP_5V.
- Commit with a short message after each finished block; push only when Kevin says.
