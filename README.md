# ReKart plans

**A go-kart built from a dead hoverboard.** Plans and code for ReKart, a drive-by-wire electric go-kart built from a used hoverboard for under $400 in parts. Made by Reboot Engineering, four seniors at Bartlett High School (Illinois), for PLTW Capstone Honors, 2026–27.

Project site and build log: https://kevsbuilds.github.io/HoverboardKart/

> **Status: in progress.** We're still building and testing. Nothing here is a finished, tested design yet. Files are added as each part is done, and the first full release is planned for May 2027.

## Safety first

This is a student project, not a certified product. It's a vehicle with a lithium battery and electronic-only braking. If you build from these plans, you do so at your own risk. Wear a helmet, keep a spotter on the wireless kill switch, test at walking speed first, and never charge the battery unattended.

## What's in here

| Folder | What goes in it | License |
|---|---|---|
| `firmware/` | Which hoverboard firmware we flash and the exact settings we use. Links only; no hoverboard firmware files. | MIT (our notes and settings) |
| `esp32/` | Main controller code (steering, pedals, speed modes, safety rules) and the wireless kill-switch remote. | MIT |
| `cad/` | STEP exports, DXFs for cut parts, drawing PDFs. | CC BY-SA 4.0 |
| `docs/` | Wiring diagram, parts list with prices, build steps, test data. | CC BY-SA 4.0 |

## How it works

- **Drivetrain:** the hoverboard's own hub motors and its two split control boards (one per wheel), reflashed with our fork of [Hoverboard-Firmware-Hack-Gen2.x](https://github.com/RoboDurden/Hoverboard-Firmware-Hack-Gen2.x) in UART bus mode.
- **Controls:** a steering wheel with an angle sensor and hall-effect pedals, read by an ESP32 that mixes steer and speed and sends each wheel's speed to its board over one shared UART bus (19200 baud, board IDs 0 and 1).
- **Safety:** brake overrides throttle, out-of-range pedals stop the kart, throttle must be zero at power-on, reverse only when stopped, a 10 mph cap with speed modes, and a wireless kill switch over ESP-NOW that stops the kart after 200 ms without a signal.
- **Frame:** 1.5 in 6061 aluminum square tube bolted together with gusset plates. No welding.

## Licenses

- Code: MIT, see `LICENSE`.
- Plans and docs: CC BY-SA 4.0, see `LICENSE-PLANS`.
- The Gen2.x motor firmware belongs to its authors; see its repo for the license.

Not affiliated with any hoverboard brand. Product and company names belong to their owners.
