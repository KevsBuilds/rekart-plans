# ELEC-control-board — spec (sheet 1: power + hoverboard bus; sheet 2: controls + sensors + screen)

ReKart main controller carrier board. KiCad 10 (Flatpak on the OptiPlex). Sheet 1: power, battery sense, hoverboard bus. Sheet 2 (`controls.kicad_sch`): pedals, AS5600, screen, wheel controls, TF-Luna.
Bus wiring copies the bench setup that passed on Nov 18/20 (`esp32/bench-keyboard`). Do not "improve" it.

## Rules
- Draw/edit KiCad on the OptiPlex only. Close the schematic in KiCad before Claude Code edits the file.
- ERC must be 0 errors after every change: `kicad-cli sch erc ELEC-control-board.kicad_sch`
- Board 5 V (J5/J6 pin 4) never connects to the ESP32. Never power the ESP32 from a hoverboard board.
- Not yet: footprints, layout (package family decided: THT, see Assembly). Layout only after the circuit is proven; PCBWay order by Feb 15.

## Assembly: through-hole (decided Nov 22)
All parts are through-hole (THT). Footprints are not assigned yet; this only fixes the package family.
1. Hand soldering with an iron, bare boards only (PCBWay free boards, no assembly): THT is the easiest to place and solder by hand, and the joints are easy to inspect by eye.
2. Perfboard v1 uses the same parts: perfboard is 2.54 mm THT, so one THT parts order covers both boards. With SMD you would need two orders or adapter boards.
3. Bench rework: THT parts can be desoldered with a pump or wick, legs can be clipped and lifted, and you can tack a bodge wire onto a lead. Small SMD (0603/0805) is harder to swap without hot air.
4. Vibration: neutral to slightly in favour of THT. Small SMD R/C parts handle vibration fine. The heavy parts (C1, C2, connectors, sockets) are THT either way, and those are the ones at risk. Hot glue or RTV on C1/C2 and strain relief on cables matter more than the choice of package.
5. Size: SMD would not shrink the board. The size is set by the ESP32 sockets (2 x 1x20, 25.4 mm apart), 12 connectors, the buck module footprint and C1/C2. The ~30 R/C/D parts fit between them as THT.

Parts with no reasonable THT option: none. R, C (ceramic + electrolytic), 1N4007/1N4148, the fuse (5x20 clip holder or radial TR5), JST-XH, pin headers, sockets and jumpers (header + shunt) all come in THT. The AS5600 is off-board on its own breakout; the buck converter is a module.

F1 rule (footprint step): first find a specific 1 A fuse whose datasheet gives a DC voltage rating >= 60 V. An AC-only rating (e.g. 250 V AC, common on 5x20 glass and TR5 fuses) does not count for a battery. Then pick the holder that fits that fuse.

F1 part (chosen Nov 22): **Eaton Bussmann S505H-1-R** (DigiKey/Mouser BK1-S505H-1-R): 5x20 mm ceramic, time-delay, 1 A, 250/500-600 V AC, **400 V DC, 1500 A interrupting at 400 V DC** (capacitor-bank test). Source: Eaton data sheet 4406 "S505H 400Vdc/500-600Vac time-delay 5x20mm fuses" (https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-s505h-vac-time-delay-fuses-data-sheet.pdf). Ratings were read from the data sheet's text via search, not from the PDF table by eye: check the 1 A row on the PDF before ordering.
- Why this one: a DC rating 6x above 60 V, ceramic body (high breaking capacity; glass is for low-energy circuits), and time-delay, so C1 charging at plug-in doesn't blow it. Alternative with the same ratings: Littelfuse 0477001.MXP (477 series, 500 V AC / 400 V DC).
- Holder: any standard 5x20 holder fits. Choose at the footprint step (KiCad has e.g. `Fuse:Fuseholder_Clip-5x20mm_Keystone_3517_Inline_P23.11x6.76mm_D1.70mm_Horizontal`, `Fuse:Fuseholder_Cylinder-5x20mm_Schurter_FAB_0031-355x_Horizontal_Closed`). For kart vibration, prefer a closed holder or clips with end stops.
- The inline 1 A fuse at the pack end (J3 note) follows the same rule: >= 60 V DC on its datasheet. The same S505H-1-R in an inline 5x20 holder works; check the holder's own voltage rating too (many automotive inline holders are 32 V).

## Battery (decided)
- Bioenno BLF-3650AS, 36 V LiFePO4 12S: 43.8 V full, 38.4 V nominal. Sponsored by Bioenno Power. Replaces the 10S Li-ion (42 V).
- 43.8 V = 88% of the boards' 50 V caps. Charge only with a 43.8 V LiFePO4 charger (the Gyroor 42 V charger won't work).
- Low-battery limits (ESP32): warn 37.2 V, limp 36.0 V, stop 34.8 V (estimates). Firmware board levels match (see Known firmware limits).
- **Until the bench test: verify the pack label shows 43.8 V charge voltage (confirms 12S).**
- Arrival test pending. Battery bench items on hold until it passes (see Bench results).

## ESP32
- Freenove ESP32-WROVER on 2 x `Connector:Conn_01x20_Socket` (J1 left, J2 right; pin 1 = antenna end). Header row spacing (J1 to J2, pin center to center): measured 25.3 mm (calipers Nov 21: outer edges 26.0, inner edges 24.6) = 25.4 mm (1.000 in, 10 x 2.54) for the footprint.
- In use: GPIO27 = bus TX, GPIO26 = bus RX, GPIO36 = battery sense. Sheet 2: pedals 32/33, AS5600 I2C 21/22, screen SPI 18/23/19 + CS 5, DC 4, BL 13, SD CS 25, wheel controls 34 (E-stop) / 39 (mode) / 14 (dir), TF-Luna 35. Every free GPIO is now used (no spare).
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
| F1 | Device:Fuse | 1A T 400VDC (Eaton Bussmann S505H-1-R, 5x20 ceramic; see F1 rule) |
| D2 | Diode:1N4007 | 1N4007 (reverse polarity) |
| D1 | Diode:1N4148 | 1N4148 |
| C1 | Device:C_Polarized | 100u/63V |
| C2 | Device:C_Polarized | 470u/16V |
| C3 | Device:C | 100n |
| R1 | Device:R | 100k |
| R2 | Device:R | **5.6k** (not 7.5k: 3.05 V at full charge is in the ESP32 ADC's non-linear zone) |
| R3 | Device:R | 1k |
| R4 | Device:R | 10k |
| JP1 | Jumper:Jumper_2_Open | 5V_EN (always pull before plugging in USB: the Freenove board has no VBUS diode) |
| — | power:GND, +BATT, +5V, +3V3; PWR_FLAG on each | |

KiCad diodes: pin 1 = K (band), pin 2 = A. C_Polarized: pin 1 = +.

## Nets
Power
- J3 sheet note: "Battery feed is ~1.5 m: inline 1 A fuse rated >= 58 V DC at the pack end, next to the main fuse."
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
- Slave's reported voltage reads 4–5.5 V high; log voltage from the master only.

## Sheet 2 (pedals, steering, screen, wheel controls, TF-Luna)
Same rules as sheet 1: label-based, short stubs, ERC 0. TBD items are marked; don't guess them.

### Parts (sheet 2)
| Ref | Symbol | Value |
|---|---|---|
| J7 | Connector_Generic:Conn_01x03 | PEDAL_THR (JST-XH 3) |
| J8 | Connector_Generic:Conn_01x03 | PEDAL_BRK (JST-XH 3) |
| J9 | Connector_Generic:Conn_01x04 | AS5600 (JST-XH 4) |
| J10 | Connector_Generic:Conn_01x14 | LCD_MSP3525 (1x14, 2.54 mm, module pin order) |
| J11 | Connector_Generic:Conn_01x06 | WHEEL_CTRL (JST-XH 6) |
| J12 | Connector_Generic:Conn_01x04 | TF_LUNA (JST-XH 4) |
| R5, R7 | Device:R | 10k, 10k |
| R6, R8 | Device:R | 12k, 12k |
| C4, C5 | Device:C | 100n, 100n |
| R9, R10 | Device:R | 4.7k, 4.7k |
| JP2 | Jumper:Jumper_2_Bridged | I2C_PU (remove if the AS5600 breakout has its own pull-ups) |
| JP3 | Jumper:Jumper_3_Bridged23 | LCD_VCC_SEL (2-3 = 5V default; 1-2 = 3V3) |
| R11 | Device:R | 10k |
| R12 | Device:R | 100 |
| R13, R14, R15 | Device:R | 10k, 10k, 10k |
| R16 | Device:R | 1k |
| C6, C7, C8 | Device:C | 100n, 100n, 100n |
| R17 | Device:R | 1k |
| R18 | Device:R | 10k |
| C9 | Device:C | 1u |

JP3 symbol is a local copy of Jumper_3_Bridged12 with the bridge on 2-3 (KiCad has no Bridged23); ERC warns "not found in library" for it.

### Nets (sheet 2)
Pedals (decided: two identical generic 3-wire hall foot throttles, 5 V in, 0.8-4.2 V out; cables 30-50 cm). Divider 10k/12k: 0.8 V -> 0.44 V, 4.2 V -> 2.29 V, short to 5 V -> 2.73 V.
- J7: 1 = +5V, 2 = GND, 3 = THR_SIG. THR_SIG -> R5 (10k) -> THR_ADC; R6 (12k) THR_ADC -> GND; C4 THR_ADC -> GND; THR_ADC -> GPIO32.
- J8: 1 = +5V, 2 = GND, 3 = BRK_SIG. BRK_SIG -> R7 (10k) -> BRK_ADC; R8 (12k) BRK_ADC -> GND; C5 BRK_ADC -> GND; BRK_ADC -> GPIO33.
- No extra pull-down: the 12k bottom resistor pulls a cut signal wire to 0 V.
- Firmware fault window (after the divider): < 0.30 V or > 2.45 V -> stop.

Steering (AS5600 breakout on the column; cable ~30 cm, keep the 4.7k pull-ups; I2C 100 kHz)
- J9: 1 = +3V3, 2 = GND, 3 = I2C_SDA (GPIO21), 4 = I2C_SCL (GPIO22).
- +3V3 -> JP2 -> I2C_PU; R9 (4.7k) I2C_PU -> I2C_SDA; R10 (4.7k) I2C_PU -> I2C_SCL. Pull JP2 if the breakout already has pull-ups.

Screen (decided: LCDwiki MSP3525, 3.5 in IPS ST7796S SPI, no touch, microSD; cable < 40 cm, SPI <= 20 MHz)
- J10 (MSP3525 order): 1 = LCD_VCC, 2 = GND, 3 = LCD_CS (GPIO5), 4 = LCD_RST, 5 = LCD_DC (GPIO4), 6 = SPI_MOSI (GPIO23), 7 = SPI_SCK (GPIO18), 8 = LCD_BL (LED), 9 = SPI_MISO (GPIO19), 10-13 = touch pins, no-connect flags, 14 = SD_CS (GPIO25).
- JP3: 1 = +3V3, 2 = LCD_VCC, 3 = +5V. Default 2-3 (5V): the module has its own regulator, so the backlight (~95 mA) stays off the ESP32 3V3 rail.
- R11 (10k) LCD_CS -> +3V3 (GPIO5 is a strapping pin, must be high at boot).
- LCD_RST: R18 (10k) LCD_RST -> +3V3; C9 (1u) LCD_RST -> GND (power-on reset, ~10 ms) -> J10.4. No GPIO, and never the ESP32 EN pin: the RST wire runs ~40 cm through the coiled wheel cable near the motor wires, and noise on EN would reset the ESP32 while driving. J1.2 (EN) stays no-connect. Sheet note: "TFT_eSPI: TFT_RST = -1 (software reset)".
- GPIO13 = LCD_BL_IO -> R12 (100) -> LCD_BL. The module switches the backlight itself (LED pin may be left open); verify polarity on arrival. Sheet note: "MSP3525 switches its backlight itself (LED pin may be left open); check polarity on arrival."

Wheel controls (from steering-wheel.md; all switch to GND)
- J11: 1 = ESTOP, 2 = MODE, 3 = DIR, 4 = GND, 5 = GND, 6 = spare (no-connect).
- E-stop, 19 mm latching, normally closed: ESTOP -> GPIO34; R13 (10k) ESTOP -> +3V3; C6 ESTOP -> GND. Normal running reads LOW; pressed OR cable cut -> HIGH -> stop.
- Mode, momentary: MODE -> GPIO39; R14 (10k) MODE -> +3V3; C7 MODE -> GND.
- Fwd/rev toggle: DIR (switch side) -> R16 (1k) -> DIR_IO -> GPIO14 (GPIO14 outputs PWM at boot; the 1k limits it into a closed switch). R15 (10k) DIR -> +3V3; C8 DIR -> GND (both on the switch side).
- The wheel e-stop is a signal only. It never switches pack current.

TF-Luna (auto braking, decided Nov 16; nose mount, ~1 m+ cable; UART, sensor streams at 100 Hz)
- J12: 1 = +5V, 2 = GND, 3 = TF_TX (sensor TX), 4 = TF_RX (sensor RX: keep the pin; no-connect flag on J12.4, not a label, so ERC has no single-pin net).
- TF_TX -> R17 (1k) -> TF_RX_IO -> GPIO35 (not GPIO39: see B). No ESP32 TX to the sensor. The sensor's config pin stays unconnected (UART mode); it is not on J12.

Not on this board: wireless kill switch (remote + separate XIAO cut-off board at the contactor, v2), power switch and main 30 A fuse (all before J3).

### Sheet 2 open questions
- A. ~~Pedal part, AS5600 cable, screen module~~ **Decided Nov 22:** screen = LCDwiki MSP3525 (J10 1x14, touch pins NC); pedals = two identical generic 3-wire hall foot throttles (J7/J8 order +5V, GND, SIG, divider 10k/12k unchanged); board in the electronics box at the base of the steering column. Cables: screen < 40 cm, AS5600 ~30 cm, pedals 30-50 cm, TF-Luna 50-70 cm, hoverboard bus ~1.3-1.6 m (< 2 m limit). Still to verify on arrival: MISO release when CS is high (SD sharing), backlight polarity.
- B. ~~GPIO39 errata~~ **Decided Nov 22: swapped.** ESP32 erratum: GPIO36/39 get ~80 ns low glitches while the ADC or Wi-Fi/ESP-NOW is active, which can corrupt UART bytes. TF-Luna RX moved to GPIO35; the mode button moved to GPIO39 (a debounced button doesn't care).
- C. ~~3V3 budget~~ **Decided Nov 22:** JP3 default = 5V (module has its own regulator); backlight ~95 mA is off the Freenove 3V3 regulator.

## Open questions
1. Passed Nov 21: bus with only GND + HB_5V between boards, 0 bad frames on both ids over ~3,900 frames (24 V bench supply). Master 78M05 output 4.9 V, link pin 4 5.0 V, 0.01 V between them under power (direct trace).
2. ~~Freenove board: does it have a diode between USB VBUS and the 5V pin?~~ **Answered Nov 21: no diode.** USB-C VBUS to the 5V header pin reads 0 both ways in diode mode (direct connection). JP1 stays; pull it before plugging in USB, or USB 5 V and the buck's +5V are tied together.
3. HB_5V sags from 4.7 V to 4.1 V with the Gyroor slave's logic on it (about 20 mA extra; bench Nov 21). The slave's 3V3 still holds at 3.3 V. Find what's in series between the master's 5 V regulator and link pin 4 before the PCB order (Feb 15). On hold: re-check on the battery once the pack is decided and passes its arrival test (see Bench results).

## Known firmware limits
Gen2.x fork `rekart-firmware`, branch `gyroor-ol20180703` (master 2.2.20.1, slave HY-A02 2.1.28.1). Design around these:
- **No DC current sensing or limit on either board.** Neither layout defines `CURRENT_DC`, so `DC_CUR_LIMIT` (15 A) never triggers and the bus reply's current is a fixed fake 0.42 A. The ESP32 must ignore it. An inline fuse on the battery lead is required.
- **No overvoltage protection.** Nothing in the firmware reacts to high bus voltage. Check the bulk capacitor voltage rating on both boards (12S LiFePO4 full = 43.8 V), and limit regen braking on a full pack.
- **Slave `ADC_BATTERY_VOLT` is uncalibrated** (library default; the master has its own value). Calibrate both boards against a meter at the item 8 bench test.
- **Battery reading starts at a 3.6 V/cell guess** (43.2 V for 12S) and filters slowly toward the real value. The ESP32 ignores low-battery levels for the first 10 s after boot.
- Board low-battery levels (12S): beep below 37.2 V, orange below 36.0 V, red below 34.8 V. `BATTERY_LOW_SHUTOFF` stays off; the ESP32 owns limp/stop.

## Bench results
- Nov 21, failsafe: USB pulled while both wheels spun: both soft-braked and stayed stopped until 'w'. Passed.
- Nov 21, master voltage calibration point 1: Eventek bench supply set to 24.0 V, master reported 23.97 V.
- On hold until the team decides on the Bioenno pack and it passes its arrival test: pack label check (43.8 V charge voltage), HB_5V re-check on the battery (open question 3), master voltage calibration point 2 (battery).

## Check commands (OptiPlex, Flatpak)
```
cd ~/dev/rekart-plans/pcb/ELEC-control-board
flatpak run --command=kicad-cli org.kicad.KiCad sch erc --severity-all -o erc.rpt ELEC-control-board.kicad_sch
flatpak run --command=kicad-cli org.kicad.KiCad sch export netlist -o netlist.net ELEC-control-board.kicad_sch
flatpak run --command=kicad-cli org.kicad.KiCad sch export pdf -o ELEC-control-board.pdf ELEC-control-board.kicad_sch
```
`erc.rpt` and `netlist.net` are scratch output; don't commit them.
