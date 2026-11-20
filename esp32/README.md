# ESP32 code

Coming soon:
- `controller/`: reads the steering angle sensor (AS5600) and hall pedals, applies the safety rules and speed modes, and sends steer and speed to the hoverboard board over UART.
- `killswitch/`: the wireless remote. Sends a heartbeat every 50 ms over ESP-NOW; the kart stops after 200 ms of silence.

Bench testing currently uses laptop keyboard commands through the ESP32.
