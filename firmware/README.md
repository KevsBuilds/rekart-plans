# Firmware

Our hoverboard (Gyroor T581) has **split boards**, one per wheel: master GD32F103C8T6, slave GD32F130C8T6. EFeru's hoverboard-firmware-hack-FOC doesn't support them, so we flash each board with our fork of [RoboDurden's Hoverboard-Firmware-Hack-Gen2.x](https://github.com/RoboDurden/Hoverboard-Firmware-Hack-Gen2.x) using an ST-Link V2.

Settings: layout 2.x.20, sub-layout 1 (gate high/low swapped on this board), block commutation, `SINGLE` mode, `REMOTE_UARTBUS` on PA2/PA3 at 19200 baud, bus id 0 (master) and 1 (slave). The ESP32 addresses each wheel by id.

This folder will hold:
- the fork, branch and exact config changes, and why
- wiring for the ST-Link and the UART bus to the ESP32
- what to check before and after flashing

We do **not** put hoverboard firmware files here: no Gen2.x builds (get the source from the project above) and no stock firmware backups (they belong to the hoverboard maker).
