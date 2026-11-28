# ELEC-control-board — spec (sheet 1: power + hoverboard bus; sheet 2: controls + sensors + screen)

ReKart main controller carrier board. KiCad 10 (OptiPlex Flatpak or Windows). Sheet 1: power, battery sense, hoverboard bus. Sheet 2 (`controls.kicad_sch`): pedals, AS5600, screen, wheel controls, TF-Luna, LED strip.
Bus wiring copies the bench setup that passed on Nov 18/20 (`esp32/bench-keyboard`). Do not "improve" it.

## Rules
- Draw/edit KiCad 10 on the OptiPlex Flatpak or Windows; close the schematic/PCB in KiCad before direct file edits.
- ERC must be 0 errors after every change: `kicad-cli sch erc ELEC-control-board.kicad_sch`
- Board 5 V (J5/J6 pin 4) never connects to the ESP32. Never power the ESP32 from a hoverboard board.
- Status (Nov 28, 2026): all 43 THT footprints assigned and `100 × 80 mm` 2-layer PCB routed (`0` DRC errors, `0` warnings, `0` unconnected, `0` schematic parity); PCBWay order by Feb 15 after bench verification.

## Assembly: through-hole (decided Nov 22)
All parts are through-hole (THT). All 43 THT footprints are assigned (see Footprints & PCB layout setup).
1. Hand soldering with an iron, bare boards only (PCBWay free boards, no assembly): THT is the easiest to place and solder by hand, and the joints are easy to inspect by eye.
2. Perfboard v1 uses the same parts: perfboard is 2.54 mm THT, so one THT parts order covers both boards. With SMD you would need two orders or adapter boards.
3. Bench rework: THT parts can be desoldered with a pump or wick, legs can be clipped and lifted, and you can tack a bodge wire onto a lead. Small SMD (0603/0805) is harder to swap without hot air.
4. Vibration: neutral to slightly in favour of THT. Small SMD R/C parts handle vibration fine. The heavy parts (C1, C2, connectors, sockets) are THT either way, and those are the ones at risk. Hot glue or RTV on C1/C2 and strain relief on cables matter more than the choice of package.
5. Size: SMD would not shrink the board. The size is set by the ESP32 sockets (2 x 1x20, 25.4 mm apart), 12 connectors, the buck module footprint and C1/C2. The ~30 R/C/D parts fit between them as THT.

Parts with no reasonable THT option: none. R, C (ceramic + electrolytic), 1N4007/1N4148, JST-XH, pin headers, sockets and jumpers (header + shunt) all come in THT. The AS5600 is off-board on its own breakout; the buck converter is a module.

## Footprints & PCB layout setup
- **Connectors:**
  - `J1, J2`: `Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical` (25.4 mm center-to-center spacing).
  - `J3` (`BATT_IN`, 43.8 V): `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal` — wire a short XT60-M pigtail with strain relief into `J3` (avoids PCB pad rip-out when unplugging a tight XT60 and keeps `J3.1`/`J3.2` schematic polarity intact).
  - `J4` (`BUCK_60V_5V`): `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-4-5.08_1x04_P5.08mm_Horizontal` — kept distinct from the five 4-pin JST-XH logic ports (`J5, J6, J8, J9, J12`) so 43.8 V `+BATT` cannot be misplugged into a logic header.
  - `J5, J6, J8, J9, J12` (4-pin): `Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical`.
  - `J7` (3-pin): `Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical`.
  - `J10` (`LCD_MSP3525`): `Connector_PinHeader_2.54mm:PinHeader_1x14_P2.54mm_Vertical`.
  - `J11` (`WHEEL_CTRL`, 6-pin): `Connector_JST:JST_XH_B6B-XH-A_1x06_P2.50mm_Vertical`.
  - `J13` (`LED_DATA`, 2-pin): `Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical`.
  - `JP1, JP2` (2-pin): `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical`.
  - `JP3` (3-pin): `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical`.
- **Passives & diodes:**
  - `C1` (`100u/63V`): `Capacitor_THT:CP_Radial_D10.0mm_P5.00mm`.
  - `C2` (`470u/16V`): `Capacitor_THT:CP_Radial_D8.0mm_P3.50mm`.
  - `C3, C4, C6–C9` (`100n`, `1u`): `Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm`.
  - `D1` (`1N4148`): `Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal`.
  - `D2` (`1N4007`): `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal`.
  - `R1–R6, R9–R19` (1/4 W axial): `Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal`.
- **PCBWay 2-layer rules & netclasses (`.kicad_pro`):**
  - Board minimums: `0.25 mm` track/clearance, `0.8 / 0.4 mm` via, `0.5 mm` copper-to-edge, `1.0 / 0.15 mm` silkscreen text.
  - `Default` (signals): `0.30 mm` track, `0.25 mm` clearance, `0.8 / 0.4 mm` via.
  - `Power_LV` (`+5V`, `+3V3`, `GND`, `ESP_5V`, `HB_5V`, `LCD_VCC`): `0.80 mm` track, `0.30 mm` clearance, `1.0 / 0.5 mm` via.
  - `Power_HV` (`+BATT`, `Net-(D2-A)`): `1.20 mm` track, `0.60 mm` clearance, `1.2 / 0.6 mm` via.
- **Starter board (`.kicad_pcb`):** `100 × 80 mm` `Edge.Cuts` outline (PCBWay `<= 100 × 100 mm` tier) with 4× M3 (`3.2 mm` NPTH) corner mounting holes inset `5 mm` (`board_only`).
- **Layout safety & copper-pour rules:**
  - `GND` pours on `F.Cu` and `B.Cu`: `Remove islands = Always`, `Thermal relief gap = 0.25 mm`, `Spoke width = 0.35 mm`.
  - `min_resolved_spokes = 1` is acceptable for low-current THT logic/sensor `GND` pads (`J7`, `J8`, `J9`, `J12`, `J2`) because their plated barrels tie to both `F.Cu` and `B.Cu`; all high-current power `GND` pads (`J3`, `J4`, `C1`, `C2`, `J5`, `J6`) must retain ≥ 2 thermal spokes.
  - Verified routed copper checks: `+BATT` / `Net-(D2-A)` at `1.20 mm` (`0.60 mm` clearance; ~2.7 A capacity vs 1 A pack-end fuse), all LV power rails (`+5V`, `ESP_5V`, `+3V3`, `LCD_VCC`, `HB_5V`) at `0.80 mm`, all signals at `0.30 mm`, `HB_5V` isolated to a single direct trace between `J5.4` and `J6.4`, and `J1`/`J2` at exact `25.40 mm` pitch.

## Battery feed fuse (decided Nov 22)
No fuse on the board (F1 removed). The only 1 A fuse is inline at the pack end, next to the main 30 A fuse:
- Holder: **Littelfuse 01500520H** inline 5x20 holder (150520 series). Datasheet (rev GD 03/20/23, checked Nov 22): 600 VAC / VDC, 20 A, fuse type 5 x 20 mm, wire "14 AWG UL3321, XLPE Insulated, Red Color", eight-inch pre-stripped leads, -40 to 105 °C. The ordering table says "Wire Range AWG 16-22", which contradicts the 14 AWG line; measure the leads on arrival. The ~20 cm leads get spliced to the ~1.5 m feed wire (crimp butt splice + heat shrink).
- Fuse: **Eaton Bussmann S505H-1-R** (DigiKey/Mouser BK1-S505H-1-R): 5x20 mm ceramic, time-delay, 1 A, 600 V AC / **400 V DC, 1500 A interrupting at 400 V DC** (capacitor-bank test). Source: Eaton Technical Data 4406, effective June 2023, Product specifications table, row S505H(-V)-1-R (https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-s505h-vac-time-delay-fuses-data-sheet.pdf); checked Nov 22 against a screenshot of the PDF. Order the cartridge S505H-1-R; -V is the axial-lead version.
- Why one fuse, at the pack end: two 1 A fuses in series on the same branch are redundant, and only the pack-end fuse protects the ~1.5 m feed wire to J3.
- Rule for any replacement: the fuse's datasheet must give a DC rating >= 60 V (an AC-only rating such as 250 V AC does not count for a battery), and the holder needs its own DC rating too. Time-delay, so C1 charging at plug-in doesn't blow it.

## Battery (decided)
Bioenno BLF-3650AS, sponsored by Bioenno Power. Replaces the 10S Li-ion (42 V). Sources: Bioenno product page + user manual rev 01/02/2024.

| | |
|---|---|
| Chemistry | LiFePO4, 12S |
| Voltage | 36 V nominal (~38.4 V plateau), **43.8 V full** |
| Capacity | **50 Ah** per the product page and the 19 kg weight; the manual's table says 20 Ah. Confirm on the label. ~1,800 Wh (36 V x 50 Ah, calculated) |
| Size / weight | 496 x 172 x 242 mm (19.6 x 6.8 x 9.6 in), 19 kg / 41.9 lb, ABS case |
| Terminals | Screw terminals; bolt size TBD (measure on arrival) |
| BMS | 50 A continuous, 100 A for 5 s. Overcurrent trips after ~2 s; reset = remove the load + connect the charger. Cell/pack voltage thresholds not published |
| Charger | 43.8 V LiFePO4 only: Bioenno BPC-3608A/C (8 A). The Gyroor 42 V charger won't work |
| Temperature | No charging below 0 °C. Operating -10 to 60 °C |

- 43.8 V = 88% of the hoverboard boards' 50 V caps.
- LiFePO4 voltage is flat until nearly empty, so pack voltage is only a coarse fuel gauge. Low-battery limits (ESP32) stay estimates: warn 37.2 V, limp 36.0 V, stop 34.8 V. Firmware board levels match (see Known firmware limits).
- Battery sense unchanged (R1 100k / R2 5.6k): 43.8 V still reads 2.32 V. No schematic change.
- **Arrival test:** label shows 43.8 V charge voltage (confirms 12S) and the capacity (50 Ah vs 20 Ah); measure the terminal bolt size. Battery bench items stay on hold until it passes (see Bench results).
- Regen / charge-current limit from motor braking: not published (see open question 4 for the mitigation).

## ESP32
- Freenove ESP32-WROVER on 2 x `Connector:Conn_01x20_Socket` (J1 left, J2 right; pin 1 = antenna end). Header row spacing (J1 to J2, pin center to center): measured 25.3 mm (calipers Nov 21: outer edges 26.0, inner edges 24.6) = 25.4 mm (1.000 in, 10 x 2.54) for the footprint.
- In use: GPIO27 = bus TX, GPIO26 = bus RX, GPIO36 = battery sense. Sheet 2: pedals 32 (thr) / 33+15 (brk HX711 DT/SCK), AS5600 I2C 21/22, screen SPI 18/23/19 + CS 5, DC 4, BL 13, SD CS 25, wheel controls 34 (E-stop) / 39 (mode) / 14 (dir), TF-Luna 35, LED strip data 2. Every free GPIO is now used (no spare).
- Avoid 0, 12, 16, 17 (16/17 = PSRAM; GPIO15/MTDO = HX711 SCK output; GPIO2 = addressable LED data output via 470 ohm — high-Z LED DIN keeps GPIO2 low/floating during flashing). Camera connector stays unplugged (shares 26/27 and others).
- Unused socket pins get a no-connect (X) until sheet 2 uses them. Write the silkscreen name of every socket pin in a text box on the sheet.

## Parts
| Ref | Symbol | Value |
|---|---|---|
| J1, J2 | Connector:Conn_01x20_Socket | ESP32_L, ESP32_R |
| J3 | Connector_Generic:Conn_01x02 | BATT_IN (after main fuse + switch) |
| J4 | Connector_Generic:Conn_01x04 | BUCK_60V_5V (LM2596HV / XL7015 class, >= 60 V in) |
| J5 | Connector_Generic:Conn_01x04 | HB_MASTER (JST-XH 4) |
| J6 | Connector_Generic:Conn_01x04 | HB_SLAVE (JST-XH 4) |
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
- J3 sheet note: "Battery feed fuse: Littelfuse 01500520H inline holder + Bussmann S505H-1-R (1 A), at the pack end next to the main 30 A fuse."
- J3.1 -> D2 (A->K) -> +BATT (direct trace, no on-board fuse). J3.2 -> GND.
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

## Sheet 2 (pedals, steering, screen, wheel controls, TF-Luna, LED strip)
Same rules as sheet 1: label-based, short stubs, ERC 0. TBD items are marked; don't guess them.

### Parts (sheet 2)
| Ref | Symbol | Value |
|---|---|---|
| J7 | Connector_Generic:Conn_01x03 | PEDAL_THR (JST-XH 3) |
| J8 | Connector_Generic:Conn_01x04 | PEDAL_BRK (JST-XH 4, HX711) |
| J9 | Connector_Generic:Conn_01x04 | AS5600 (JST-XH 4) |
| J10 | Connector_Generic:Conn_01x14 | LCD_MSP3525 (1x14, 2.54 mm, module pin order) |
| J11 | Connector_Generic:Conn_01x06 | WHEEL_CTRL (JST-XH 6) |
| J12 | Connector_Generic:Conn_01x04 | TF_LUNA (JST-XH 4) |
| R5 | Device:R | 10k |
| R6 | Device:R | 12k |
| C4 | Device:C | 100n |
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
| J13 | Connector_Generic:Conn_01x02 | LED_DATA (JST-XH 2, WS2812B/WS2815) |
| R19 | Device:R | 470 |

JP3 symbol is a local copy of Jumper_3_Bridged12 with the bridge on 2-3 (KiCad has no Bridged23); ERC warns "not found in library" for it.

### Nets (sheet 2)
Pedals (throttle = KY-035 49E analog Hall sensor, 5 V in, cables 30-50 cm; brake = 150 kg load cell + HX711 amplifier, 3.3 V logic, modded to 80 Hz):
- J7 (throttle): 1 = +5V, 2 = GND, 3 = THR_SIG. THR_SIG -> R5 (10k) -> THR_ADC; R6 (12k) THR_ADC -> GND; C4 THR_ADC -> GND; THR_ADC -> GPIO32. No extra pull-down: the 12k bottom resistor pulls a cut signal wire to 0 V. Firmware fault window (after the divider): < 0.30 V or > 2.45 V -> stop.
- J8 (brake HX711): 1 = +3V3, 2 = GND, 3 = BRK_DT (GPIO33), 4 = BRK_SCK (GPIO15). Firmware enables INPUT_PULLUP on BRK_DT and treats HX711 ready timeout (> 100 ms) as a brake fault -> stop.

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

LED strip (addressable WS2812B-V5 / WS2815, external fused 5 V / 12 V buck — never power strips from this board's +5V)
- J13: 1 = GND, 2 = LED_DATA. LED_DATA -> R19 (470) -> LED_IO -> GPIO2.

Not on this board: wireless kill switch (remote + separate XIAO cut-off board at the contactor, v2), power switch, main 30 A fuse and the 1 A battery-feed fuse (all before J3).

### Sheet 2 open questions
- A. ~~Pedal part, AS5600 cable, screen module~~ **Decided Nov 22:** screen = LCDwiki MSP3525 (J10 1x14, touch pins NC); pedals = two identical generic 3-wire hall foot throttles (J7/J8 order +5V, GND, SIG, divider 10k/12k unchanged); board in the electronics box at the base of the steering column. Cables: screen < 40 cm, AS5600 ~30 cm, pedals 30-50 cm, TF-Luna 50-70 cm, hoverboard bus ~1.3-1.6 m (< 2 m limit). Still to verify on arrival: MISO release when CS is high (SD sharing), backlight polarity. (Superseded Nov 28: throttle = KY-035 49E on J7; brake = 150 kg load cell + HX711 on 4-pin J8 +3V3/GND/GPIO33/GPIO15, R7/R8/C5 removed; addressable LED strip data added on 2-pin J13 + R19 470 -> GPIO2.)
- B. ~~GPIO39 errata~~ **Decided Nov 22: swapped.** ESP32 erratum: GPIO36/39 get ~80 ns low glitches while the ADC or Wi-Fi/ESP-NOW is active, which can corrupt UART bytes. TF-Luna RX moved to GPIO35; the mode button moved to GPIO39 (a debounced button doesn't care).
- C. ~~3V3 budget~~ **Decided Nov 22:** JP3 default = 5V (module has its own regulator); backlight ~95 mA is off the Freenove 3V3 regulator.

## Open questions
1. Passed Nov 21: bus with only GND + HB_5V between boards, 0 bad frames on both ids over ~3,900 frames (24 V bench supply). Master 78M05 output 4.9 V, link pin 4 5.0 V, 0.01 V between them under power (direct trace).
2. ~~Freenove board: does it have a diode between USB VBUS and the 5V pin?~~ **Answered Nov 21: no diode.** USB-C VBUS to the 5V header pin reads 0 both ways in diode mode (direct connection). JP1 stays; pull it before plugging in USB, or USB 5 V and the buck's +5V are tied together.
3. HB_5V sags from 4.7 V to 4.1 V with the Gyroor slave's logic on it (about 20 mA extra; bench Nov 21). The slave's 3V3 still holds at 3.3 V. Find what's in series between the master's 5 V regulator and link pin 4 before the PCB order (Feb 15). On hold: re-check on the battery once the pack is decided and passes its arrival test (see Bench results).
4. **Regen charge-current limit: not published, and there is no Bioenno contact, so it stays unknown.** Mitigation: a deceleration ramp limits regen, and the ESP32 logs the master's bus-reply voltage on hard stops and flags anything > 46 V (50 V caps on the hoverboard boards).

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

## Pre-order verification & bench bring-up checklist
- **Verified PCB geometry & fit (`100.0 × 80.0 mm`, 2-layer):**
  - `J1` (left, `X = 137.30`) and `J2` (right, `X = 162.70`), both `rot = 0`, pin 1 at top (`Y = 65.00`) and pin 20 at bottom (`Y = 113.26`): exact `25.4000 mm` spacing, top-view non-mirrored Freenove ESP32-WROVER pinout. Leave ~6 mm box clearance above the top edge for the Wi-Fi antenna (~2–4 mm overhang past `Y = 60.0`); bottom USB-C has `26.7 mm` runway to the bottom edge.
  - Screw terminals: `J3` faces UP (`1.67 mm` inside top edge), `J4` faces LEFT (`1.67 mm` inside left edge). All other connectors sit inside `Edge.Cuts`, zero tall parts sit inside the ESP32 shadow, and all 4 M3 corner holes (`H1–H4`) have `> 7 mm` clearance to every pad.
- **PCBWay manufacturing check (2-layer, `1.6 mm` FR4, `1 oz` Cu, `<= 100 × 100 mm` tier):**
  - Min track `0.30 mm` (PCBWay min `0.15 mm`), min via `0.40 mm` drill / `0.20 mm` ring (min `0.30 / 0.13 mm`), min THT `0.80 mm` drill / `0.35 mm` ring.
  - Saved PCB status (Nov 28, 2026): `J13`/`R19` are routed and `kicad-cli` DRC passed with `0` violations, `0` unconnected items, and `0` schematic parity issues. Before PCBWay order: do a final `Alt+3` 3D check, add any optional silkscreen labels, and inspect Gerbers + Excellon drills in KiCad Gerber Viewer and PCBWay's online viewer.
- **Parts-to-footprint match check:**
  - `J3`/`J4`: 5.08 mm pitch screw terminals (`1.3 mm` drill); `C1`: `10 mm` dia / `5.0 mm` pitch; `C2`: `8 mm` dia / `3.5 mm` pitch; `C3, C4, C6–C9`: `5.0 mm` pitch; `R1–R6, R9–R19`: 1/4 W axial (`10.16 mm` pitch); `J1`/`J2`: tack-solder corner pins with the ESP32 plugged into both sockets so rows stay parallel; verify 6-pin JST-XH kit pitch (`12.5 mm` vs `12.7 mm` pin 1–6).
- **Bench bring-up sequence (on board arrival):**
  1. Unpowered continuity check: no shorts on `+BATT`, `+5V`, `+3V3` to `GND`; confirm `HB_5V` is open (`∞ Ω`) to `+5V`, `ESP_5V`, and `+3V3`.
  2. First power-up (24 V / 1 A bench limit, ESP32 unplugged, `JP1` pulled): verify `+BATT` (~23.3 V after `D2`), `VBAT_SENSE` at `J1.3` (~1.23 V), `+5V` = `5.0 V`, `HB_5V` = `0 V`.
  3. Set `JP3` shunt on `2–3` (`+5V`); always pull `JP1` before plugging USB-C into the ESP32.
  4. Bench-test HX711 (`J8`) at `3.3 V` with the `80 Hz / RATE` mod and verify timeout fault stop; bench-test LED strip (`J13`) powered from a separate fused buck (confirm USB flashing still works with `J13` connected; add an inline 74AHCT125 or sacrificial pixel at the strip buck only if an older 5 V WS2812B glitches on a long wire).
  5. Hoverboard power order: power motor boards before ESP32, unplug ESP32 first.

## Check commands (OptiPlex, Flatpak)
```
cd ~/dev/rekart-plans/pcb/ELEC-control-board
flatpak run --command=kicad-cli org.kicad.KiCad sch erc --severity-all -o erc.rpt ELEC-control-board.kicad_sch
flatpak run --command=kicad-cli org.kicad.KiCad sch export netlist -o netlist.net ELEC-control-board.kicad_sch
flatpak run --command=kicad-cli org.kicad.KiCad sch export pdf -o ELEC-control-board.pdf ELEC-control-board.kicad_sch
```
`erc.rpt` and `netlist.net` are scratch output; don't commit them.
