# ELEC-control-board — Sheet 1 spec (Power + Hoverboard Bus)

ReKart main controller carrier board. KiCad 10 (Flatpak on the OptiPlex). Sheet 1 only: power, battery sense, hoverboard bus.
Bus wiring copies the bench setup that passed on Nov 18/20 (`esp32/bench-keyboard`). Do not "improve" it.

## Rules
- Draw/edit KiCad on the OptiPlex only. Close the schematic in KiCad before Claude Code edits the file.
- ERC must be 0 errors after every change: `kicad-cli sch erc ELEC-control-board.kicad_sch`
- Board 5 V (J5/J6 pin 4) never connects to the ESP32. Never power the ESP32 from a hoverboard board.
- Skip on sheet 1: pedals, AS5600, screen, buttons (sheet 2), footprints, layout. Layout only after the circuit is proven; PCBWay order by Feb 15.

## ESP32
- Freenove ESP32-WROVER on 2 x `Connector:Conn_01x20_Socket` (J1 left, J2 right; pin 1 = antenna end). Header spacing: measure with calipers before footprints.
- In use: GPIO27 = bus TX, GPIO26 = bus RX, GPIO36 = battery sense. Later (sheet 2): pedals 32/33, AS5600 I2C 21/22, screen SPI 18/23/19 + CS 5, DC 4, BL 13, SD CS 25.
- Avoid 0, 2, 12, 15, 16, 17 (16/17 = PSRAM). Camera connector stays unplugged (shares 26/27 and others).
- Unused socket pins get a no-connect (X) until sheet 2 uses them. Write the silkscreen name of every socket pin in a text box on the sheet.

## Parts
| Ref | Symbol | Value |
|---|---|---|
| J1, J2 | Connector:Conn_01x20_Socket | ESP32_L, ESP32_R |
| J3 | Connector_Generic:Conn_01x02 | BATT_IN (after main fuse + switch) |
| J4 | Connector_Generic:Conn_01x04 | BUCK_60V_5V (LM2596HV / XL7015 class, >= 60 V in) |
| J5 | Connector_Generic:Conn_01x04 | HB_MASTER (JST-XH 4) |
| J6 | Connector_Generic:Conn_01x04 | HB_SLAVE (JST-XH 4) |
| F1 | Device:Fuse | 1A 60VDC (part TBD, >= 60 V DC rating) |
| D2 | Diode:1N4007 | 1N4007 (reverse polarity) |
| D1 | Diode:1N4148 | 1N4148 |
| C1 | Device:C_Polarized | 100u/63V |
| C2 | Device:C_Polarized | 470u/16V |
| C3 | Device:C | 100n |
| R1 | Device:R | 100k |
| R2 | Device:R | **5.6k** (not 7.5k: 3.05 V at full charge is in the ESP32 ADC's non-linear zone) |
| R3 | Device:R | 1k |
| R4 | Device:R | 10k |
| JP1 | Jumper:Jumper_2_Open | 5V_EN (pull before plugging in USB until the Freenove VBUS diode is confirmed) |
| — | power:GND, +BATT, +5V, +3V3; PWR_FLAG on each | |

KiCad diodes: pin 1 = K (band), pin 2 = A. C_Polarized: pin 1 = +.

## Nets
Power
- J3.1 -> F1 -> D2 (A->K) -> +BATT. J3.2 -> GND.
- C1 + to +BATT, - to GND.
- J4.1 VIN+ = +BATT; J4.2 VIN- = GND; J4.3 VOUT+ = +5V; J4.4 VOUT- = GND.
- C2 + to +5V, - to GND.
- +5V -> JP1 -> ESP_5V -> ESP32 5V pin.

Battery sense
- +BATT -> R1 -> VBAT_SENSE; R2 VBAT_SENSE -> GND; C3 VBAT_SENSE -> GND; VBAT_SENSE -> GPIO36.
- 43.8 V -> 2.32 V; 50 V -> 2.65 V; 30 V -> 1.59 V. Reads ~0.7 V low (D2): calibrate one scale factor against the master's bus-reply voltage.

Hoverboard bus (19200 8N1, master id 0, slave id 1)
- GPIO27 -> BUS_TX -> R3 (1k) -> HB_PA3 -> J5.3 and J6.3 (both boards' PA3 = MCU pin 13, bottom edge, 1st from left).
- GPIO26 = BUS_RX -> J5.2 (master PA2 = MCU pin 12, left edge, 12th from top) directly.
- BUS_RX -> D1.2 (A); D1.1 (K, band) -> S_PA2 -> J6.2 (slave PA2). Band toward the slave.
- R4 (10k) BUS_RX -> +3V3 (side branch, never in series).
- J5.1, J6.1 = GND.
- J5.4 <-> J6.4 = net **HB_5V** (master's 5 V feeds the slave's logic; the slave has no power switch). This replaces the 5 V wire of the stock board-to-board cable. HB_5V never touches +5V or ESP_5V.
- The board-to-board data wires are NOT reproduced: each board's PA2/PA3 goes only to the bus as listed above.
- J5/J6 pin order = the boards' link connector, top view left to right: GND, PA2, PA3, 5V. Cable is straight-through (NOT the crossed stock cable). Continuity-check which end is pin 1.

## Open questions
1. Bench check before the PCB: run the bus with HB_5V + GND as the only board-to-board wires (stock cable unplugged) and confirm 0 bad frames on both ids.
2. Battery: a Bioenno LiFePO4 12S (43.8 V full) pack would replace the settled 10S Li-ion (42 V). 88% of the boards' 50 V caps; needs a 43.8 V LiFePO4 charger (Gyroor 42 V charger won't work); low-battery limits change (estimates: warn 37.2 V, limp 36.0 V, stop 34.8 V). Team decision. The circuit works for either.
3. Freenove board: does it have a diode between USB VBUS and the 5V pin? Decides whether JP1 stays.

## Check commands (OptiPlex, Flatpak)
```
cd ~/dev/rekart-plans/pcb/ELEC-control-board
flatpak run --command=kicad-cli org.kicad.KiCad sch erc --severity-all -o erc.rpt ELEC-control-board.kicad_sch
flatpak run --command=kicad-cli org.kicad.KiCad sch export netlist -o netlist.net ELEC-control-board.kicad_sch
flatpak run --command=kicad-cli org.kicad.KiCad sch export pdf -o ELEC-control-board.pdf ELEC-control-board.kicad_sch
```
`erc.rpt` and `netlist.net` are scratch output; don't commit them.
