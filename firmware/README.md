# Firmware

We flash the hoverboard's control board with [hoverboard-firmware-hack-FOC](https://github.com/EFeru/hoverboard-firmware-hack-FOC) (and forks for split boards) using an ST-Link V2.

This folder will hold:
- which variant and fork we use, and why
- our exact build settings (config changes)
- wiring for the ST-Link and the UART link to the ESP32
- what to check before and after flashing

We do **not** put hoverboard firmware files here: not the FOC builds (GPL-3.0, get them from the project above) and not stock firmware backups (they belong to the hoverboard maker).
