# Bench test: keyboard drive

Drives both hoverboard wheels from a laptop keyboard through the ESP32, over the Gen2.x UART bus (19200 baud, master id 0, slave id 1). For the bench only: the speed and steering are capped at 300 of 1000.

## Run it
```
cd esp32/bench-keyboard
pio run -t upload
pio device monitor
```
Keys: `w`/`s` speed, `a`/`d` steer, `c` center, space = smooth stop, `x` = instant stop, `f` = flip the right wheel, `?` = help. Keys work without Enter in `pio device monitor` (not in the Arduino IDE monitor).

## Before powering
- Bench supply 24 V, current limit 1.0 A. Wheels off the ground.
- Check the bus wiring at the chip legs (see the wiring list at the top of `src/main.cpp`).
- Boards on first, then plug in the ESP32. ESP32 off first when shutting down.

## Pass checks
1. Both wheels show `ok` and the `bad` count stays at 0.
2. `w` x2: both wheels spin forward smoothly, same direction. If one spins backward, press `f`.
3. `a` / `d`: one wheel speeds up, the other slows.
4. Space: both wheels ramp down to a stop in under 1 s.
5. Unplug the ESP32's USB while spinning: both wheels soft-brake within 0.5 s (board failsafe).
6. `odom` counts about 90 per wheel turn (turn a wheel by hand to check).
