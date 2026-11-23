# ELEC-control-board — Sheet 1 spec (Power + Hoverboard Bus)

ReKart main controller carrier board. KiCad 10 (Flatpak on the OptiPlex). Sheet 1 only: power, battery sense, hoverboard bus.
Bus wiring copies the bench setup that passed on Nov 18/20 (`esp32/bench-keyboard`). Do not "improve" it.

## Rules
- Draw/edit KiCad on the OptiPlex only. Close the schematic in KiCad before Claude Code edits the file.
- ERC must be 0 errors after every change: `kicad-cli sch erc ELEC-control-board.kicad_sch`
- Board 5 V (J5/J6 pin 4) never connects to the ESP32. Never power the ESP32 from a hoverboard board.
- Skip on sheet 1: pedals, AS5600, screen, buttons (sheet 2), footprints, layout. Layout only after the circuit is proven; PCBWay order by Feb 15.

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
| JP1 | Jumper:Jumper_2_Open | 5V_EN (always pull before plugging in USB: the Freenove board has no VBUS diode) |
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
- Slave's reported voltage reads 4–5.5 V high; log voltage from the master only.

## Sheet 2 (pedals, steering, screen, wheel controls, TF-Luna)
Same rules as sheet 1: label-based, short stubs, ERC 0. TBD items are marked; don't guess them.

### Parts (sheet 2)
| Ref | Symbol | Value |
|---|---|---|
| J7 | Connector_Generic:Conn_01x03 | PEDAL_THR (JST-XH 3) |
| J8 | Connector_Generic:Conn_01x03 | PEDAL_BRK (JST-XH 3) |
| J9 | Connector_Generic:Conn_01x04 | AS5600 (JST-XH 4) |
| J10 | Connector_Generic:Conn_01x10 | LCD_ST7796S (1x10) |
| J11 | Connector_Generic:Conn_01x06 | WHEEL_CTRL (JST-XH 6) |
| J12 | Connector_Generic:Conn_01x04 | TF_LUNA (JST-XH 4) |
| R5, R7 | Device:R | 10k, 10k |
| R6, R8 | Device:R | 12k, 12k |
| C4, C5 | Device:C | 100n, 100n |
| R9, R10 | Device:R | 4.7k, 4.7k |
| JP2 | Jumper:Jumper_2_Bridged | I2C_PU (remove if the AS5600 breakout has its own pull-ups) |
| JP3 | Jumper:Jumper_3_Bridged12 | LCD_VCC_SEL (1-2 = 3V3 default; 2-3 = 5V only if the module has an onboard regulator) |
| R11 | Device:R | 10k |
| R12 | Device:R | 100 |
| R13, R14, R15 | Device:R | 10k, 10k, 10k |
| R16 | Device:R | 1k |
| C6, C7, C8 | Device:C | 100n, 100n, 100n |
| R17 | Device:R | 1k |
| R18 | Device:R | 10k |
| C9 | Device:C | 1u |

### Nets (sheet 2)
Pedals (part TBD; assume 5 V supply, 0.8-4.2 V out). Divider 10k/12k: 0.8 V -> 0.44 V, 4.2 V -> 2.29 V, short to 5 V -> 2.73 V.
- J7: 1 = +5V, 2 = GND, 3 = THR_SIG. THR_SIG -> R5 (10k) -> THR_ADC; R6 (12k) THR_ADC -> GND; C4 THR_ADC -> GND; THR_ADC -> GPIO32.
- J8: 1 = +5V, 2 = GND, 3 = BRK_SIG. BRK_SIG -> R7 (10k) -> BRK_ADC; R8 (12k) BRK_ADC -> GND; C5 BRK_ADC -> GND; BRK_ADC -> GPIO33.
- No extra pull-down: the 12k bottom resistor pulls a cut signal wire to 0 V.
- Firmware fault window (after the divider): < 0.30 V or > 2.45 V -> stop.

Steering (AS5600 breakout on the column; cable length TBD, assume up to ~1 m; I2C 100 kHz)
- J9: 1 = +3V3, 2 = GND, 3 = I2C_SDA (GPIO21), 4 = I2C_SCL (GPIO22).
- +3V3 -> JP2 -> I2C_PU; R9 (4.7k) I2C_PU -> I2C_SDA; R10 (4.7k) I2C_PU -> I2C_SCL. Pull JP2 if the breakout already has pull-ups.

Screen (3.5 in IPS ST7796S SPI, no touch, microSD; exact module TBD; cable < 40 cm, SPI <= 20 MHz)
- J10: 1 = LCD_VCC, 2 = GND, 3 = LCD_CS (GPIO5), 4 = LCD_RST, 5 = LCD_DC (GPIO4), 6 = SPI_MOSI (GPIO23), 7 = SPI_SCK (GPIO18), 8 = LCD_BL, 9 = SPI_MISO (GPIO19), 10 = SD_CS (GPIO25).
- JP3: 1 = +3V3, 2 = LCD_VCC, 3 = +5V. Default 1-2 (3V3).
- R11 (10k) LCD_CS -> +3V3 (GPIO5 is a strapping pin, must be high at boot).
- LCD_RST: R18 (10k) LCD_RST -> +3V3; C9 (1u) LCD_RST -> GND (power-on reset, ~10 ms) -> J10.4. No GPIO, and never the ESP32 EN pin: the RST wire runs ~40 cm through the coiled wheel cable near the motor wires, and noise on EN would reset the ESP32 while driving. J1.2 (EN) stays no-connect. Sheet note: "TFT_eSPI: TFT_RST = -1 (software reset)".
- GPIO13 = LCD_BL_IO -> R12 (100) -> LCD_BL. Assumes the module has its own backlight transistor. Sheet note: "If the module has no BL transistor, add a BS170 low-side switch before ordering."

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
- A. TBD: pedal part, AS5600 cable length, screen module (check for a BL transistor, VCC range, and whether the ST7796S releases MISO when its CS is high, or the SD card can't share SPI_MISO).
- B. ~~GPIO39 errata~~ **Decided Nov 22: swapped.** ESP32 erratum: GPIO36/39 get ~80 ns low glitches while the ADC or Wi-Fi/ESP-NOW is active, which can corrupt UART bytes. TF-Luna RX moved to GPIO35; the mode button moved to GPIO39 (a debounced button doesn't care).
- C. 3V3 budget: with JP3 on 3V3, the screen (backlight from VCC on most modules) and the microSD card run from the Freenove board's 3V3 regulator, on top of the ESP32's Wi-Fi peaks. Check the module's VCC current and the regulator rating before choosing 3V3 or 5V.

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
