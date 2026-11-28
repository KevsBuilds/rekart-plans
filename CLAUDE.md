# ReKart — notes for Claude

Hoverboard-based electric go-kart: Reboot Engineering's PLTW senior capstone, **due May 1, 2027**.
Motor boards run our fork of **Hoverboard-Firmware-Hack-Gen2.x** (UART bus mode), not ZS-X11H
controllers. Project overview, safety rules and licenses: [README.md](README.md).

## Repo map
| Dir | What |
|---|---|
| `pcb/` | KiCad 10 boards, one folder each; `pcb/check.sh` runs the checks. Board rules: [pcb/ELEC-control-board/CLAUDE.md](pcb/ELEC-control-board/CLAUDE.md), spec: [SPEC.md](pcb/ELEC-control-board/SPEC.md) |
| `firmware/` | Gen2.x fork, settings and flashing notes (links only, no firmware binaries): [firmware/README.md](firmware/README.md) |
| `esp32/` | ESP32 main controller and kill-switch code; `bench-keyboard/` is the current bench test (PlatformIO) |
| `cad/` | Fusion exports: STEP, DXF, drawing PDFs (after the Dec 20, 2026 CAD freeze) |
| `docs/` | Wiring diagram, parts list, build guide, test data |

## Division of work
- **Kevin** draws schematics and routes PCBs in KiCad 10 (OptiPlex Flatpak or Windows KiCad 10).
- **Claude** runs `pcb/check.sh`, reads the reports, and proposes fixes (by ref + pin, against SPEC.md).
- Edit a `.kicad_sch` only when Kevin asks: one change at a time, KiCad closed on that file,
  then re-run `pcb/check.sh` and report. Board-specific rules are in that board's CLAUDE.md.

## Firmware
- Claude edits and compiles on the OptiPlex.
- Flashing (ST-Link on the hoverboard boards, USB upload to the ESP32) and bench tests happen
  only on Kevin's Windows PC. **Never attempt to flash or upload** (`pio run -t upload`, `st-flash`,
  OpenOCD, etc.), even if a README shows the command.
- How Kevin flashes on Windows (ST-Link, speed 200, CPUTAPID 0, verify): [docs/notes/flashing.md](docs/notes/flashing.md).

## Safety (stop and ask)
Never change any of these without flagging it clearly and waiting for Kevin's OK:
- motor current limits, speed caps, ramp/brake behavior
- battery / BMS values (cell count, voltage thresholds, low-battery limits, fuse ratings)
- kill-switch logic or timeouts, failsafes, link-loss handling, throttle/brake interlocks

## Git
- Small commits with clear messages; author = Kevin's GitHub noreply email (global git config).
- Never force-push. Never push without Kevin's OK.
- **The repo is public:** no secrets, tokens, email addresses, phone numbers, addresses or other
  personal data, and no hoverboard firmware binaries or stock backups (see `.gitignore`).
- Generated output (`pcb/*/reports/`, `.pio/`, `build/`) stays out of git.

## Commands
```bash
pcb/check.sh                       # every pcb/*/ with a .kicad_pro
pcb/check.sh ELEC-control-board    # one board
```
Writes `<board>/reports/` (erc/drc .json + .rpt, bom.csv, netlist.net). Prints a summary
table; exits 1 on any error-severity violation (warnings don't fail).

## Build (hoverboard firmware, compile only)
Source: `~/dev/rekart-firmware` (our Gen2.x fork), branch `gyroor-ol20180703`. PlatformIO is
installed for kevin via pipx (`~/.local/bin/pio`).
```bash
cd ~/dev/rekart-firmware/HoverBoardGigaDevice
pio run -e genericGD32F103C8 -e genericGD32F130C8   # build only: never add -t upload
```
| Board | Env | Layout | Output |
|---|---|---|---|
| Master (Gyroor, GD32F103, bus id 0) | `genericGD32F103C8` | 2.2.20 sub 1 | `.pio/build/genericGD32F103C8/firmware.bin` |
| Slave (HY-A02, GD32F130, bus id 1) | `genericGD32F130C8` | 2.1.28 sub 1 | `.pio/build/genericGD32F130C8/firmware.bin` |

Layout per chip is chosen in `Inc/config.h`. Copy the `.bin` files to Kevin's PC for flashing.
