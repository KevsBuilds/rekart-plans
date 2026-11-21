// ReKart bench test: drive both wheels from the laptop keyboard.
//
// Wiring (working bus from Nov 18, see hoverboard-specs):
//   GPIO27 (TX) -> 1 k -> both boards' PA3
//   Master PA2 -> GPIO26 (RX) direct; slave PA2 -> 1N4148 (band toward slave) -> GPIO26
//   10 k from GPIO26 to 3.3 V, GND shared. Never power the ESP32 from the board's 5 V.
// Power the boards BEFORE the ESP32, unplug the ESP32 FIRST.
// Bench supply: 24 V, current limit 1.0 A.
//
// Keys (pio device monitor sends each key right away, no Enter needed):
//   w / s   speed up / down (steps of 50)
//   a / d   steer left / right (steps of 50)
//   c       center the steering
//   space   smooth stop (speed and steer to 0 through the ramp)
//   x       instant stop (skips the ramp)
//   f       flip the right wheel's direction if it spins the wrong way
//   ?       print the keys again
//
// Protocol (Gen2.x REMOTE_UARTBUS, 19200 8N1):
//   command 8 bytes:  '/', type 0, id, int16 speed (+-1000), uint8 wState, CRC16 (low byte first)
//   reply  15 bytes:  0xCD 0xAB, id, int16 km/h x100, uint16 V x100, int16 A x100, int32 odom, CRC16
//   CRC-16/XMODEM over everything before the CRC. Board failsafe: no frame for 500 ms -> soft brake.
//   wState bits 64 (disable) and 128 (shut off) are never set here.

#include <Arduino.h>

// ---------- settings ----------
static const int PIN_RX = 26;
static const int PIN_TX = 27;
static const uint32_t BUS_BAUD = 19200;

static const uint8_t ID_LEFT = 0;    // Gyroor master
static const uint8_t ID_RIGHT = 1;   // Gyroor slave
static bool invertRight = true;      // motors are mirror-mounted; press 'f' to flip if needed

static const int16_t SPEED_LIMIT = 300;  // bench cap (full scale is 1000)
static const int16_t STEER_LIMIT = 300;
static const int16_t STEP = 50;          // per key press
static const int16_t RAMP_UP = 15;       // max change per 25 ms frame while speeding up (~600/s)
static const int16_t RAMP_DOWN = 30;     // faster when slowing down (~1200/s)
static const uint32_t FRAME_MS = 25;     // alternate wheels -> each board gets a frame every 50 ms
static const uint8_t WSTATE = 0;         // LEDs off; never 64 or 128

HardwareSerial Bus(2);

// ---------- state ----------
static int16_t targetSpeed = 0, targetSteer = 0;
static int16_t speedNow = 0, steerNow = 0;

struct Feedback {
  float kmh = 0, volts = 0;
  int32_t odom = 0;
  uint32_t good = 0, bad = 0;
  uint32_t lastMs = 0;
};
static Feedback fb[2];

// ---------- CRC-16/XMODEM (poly 0x1021, init 0) ----------
static uint16_t crc16(const uint8_t *data, size_t len) {
  uint16_t crc = 0;
  for (size_t i = 0; i < len; i++) {
    crc ^= (uint16_t)data[i] << 8;
    for (int b = 0; b < 8; b++) crc = (crc & 0x8000) ? (crc << 1) ^ 0x1021 : (crc << 1);
  }
  return crc;
}

static void sendSpeed(uint8_t id, int16_t speed) {
  uint8_t f[8];
  f[0] = '/';
  f[1] = 0;                 // type 0 = speed command
  f[2] = id;
  f[3] = speed & 0xFF;
  f[4] = (speed >> 8) & 0xFF;
  f[5] = WSTATE & 0x3F;     // mask: bits 64 and 128 can never go out
  uint16_t c = crc16(f, 6);
  f[6] = c & 0xFF;          // low byte first
  f[7] = c >> 8;
  Bus.write(f, sizeof f);
}

// Reply parser: scans for 0xCD 0xAB, then collects 15 bytes.
static uint8_t rx[15];
static uint8_t rxPos = 0;

static void readReplies() {
  while (Bus.available()) {
    uint8_t b = Bus.read();
    if (rxPos == 0 && b != 0xCD) continue;
    if (rxPos == 1 && b != 0xAB) { rxPos = (b == 0xCD) ? 1 : 0; continue; }
    rx[rxPos++] = b;
    if (rxPos < sizeof rx) continue;
    rxPos = 0;
    uint8_t id = rx[2];
    if (id > 1) continue;
    uint16_t c = rx[13] | (rx[14] << 8);
    if (crc16(rx, 13) != c) { fb[id].bad++; continue; }
    int16_t kmh = rx[3] | (rx[4] << 8);
    uint16_t v = rx[5] | (rx[6] << 8);
    int32_t odom = (int32_t)(rx[9] | (rx[10] << 8) | ((uint32_t)rx[11] << 16) | ((uint32_t)rx[12] << 24));
    fb[id].kmh = kmh / 100.0f;
    fb[id].volts = v / 100.0f;
    fb[id].odom = odom;
    fb[id].good++;
    fb[id].lastMs = millis();
  }
}

static int16_t clampi(int32_t v, int16_t lo, int16_t hi) { return v < lo ? lo : (v > hi ? hi : v); }

static int16_t rampToward(int16_t now, int16_t target) {
  // Slowing down (moving toward 0 or reversing) uses the faster ramp.
  bool slowing = (target == 0) || ((now > 0) != (target > 0)) || (abs(target) < abs(now));
  int16_t step = slowing ? RAMP_DOWN : RAMP_UP;
  if (target > now) return min<int16_t>(target, now + step);
  if (target < now) return max<int16_t>(target, now - step);
  return now;
}

static void printHelp() {
  Serial.println(F("\nReKart keyboard bench test"));
  Serial.println(F("  w/s speed +/-   a/d steer   c center   space smooth stop   x instant stop"));
  Serial.println(F("  f flip right wheel   ? help"));
  Serial.printf("  Bench caps: speed +-%d, steer +-%d (of 1000)\n\n", SPEED_LIMIT, STEER_LIMIT);
}

static void handleKey(char k) {
  switch (k) {
    case 'w': targetSpeed = clampi(targetSpeed + STEP, -SPEED_LIMIT, SPEED_LIMIT); break;
    case 's': targetSpeed = clampi(targetSpeed - STEP, -SPEED_LIMIT, SPEED_LIMIT); break;
    case 'a': targetSteer = clampi(targetSteer - STEP, -STEER_LIMIT, STEER_LIMIT); break;
    case 'd': targetSteer = clampi(targetSteer + STEP, -STEER_LIMIT, STEER_LIMIT); break;
    case 'c': targetSteer = 0; break;
    case ' ': targetSpeed = 0; targetSteer = 0; break;
    case 'x': targetSpeed = targetSteer = speedNow = steerNow = 0; Serial.println(F("INSTANT STOP")); break;
    case 'f': invertRight = !invertRight; Serial.printf("Right wheel inverted: %s\n", invertRight ? "yes" : "no"); break;
    case '?': printHelp(); break;
    default: return;
  }
  Serial.printf("target speed %4d  steer %4d\n", targetSpeed, targetSteer);
}

void setup() {
  Serial.begin(115200);
  Bus.begin(BUS_BAUD, SERIAL_8N1, PIN_RX, PIN_TX);
  delay(300);
  // Safety rule: start at zero no matter what.
  targetSpeed = targetSteer = speedNow = steerNow = 0;
  printHelp();
}

void loop() {
  static uint32_t lastFrame = 0, lastPrint = 0;
  static bool sendLeft = true;

  while (Serial.available()) handleKey((char)tolower(Serial.read()));
  readReplies();

  uint32_t now = millis();
  if (now - lastFrame >= FRAME_MS) {
    lastFrame = now;
    if (sendLeft) {  // ramp once per full cycle (both wheels)
      speedNow = rampToward(speedNow, targetSpeed);
      steerNow = rampToward(steerNow, targetSteer);
    }
    // Mix: steering right (+) speeds up the left wheel and slows the right.
    int16_t left = clampi(speedNow + steerNow, -1000, 1000);
    int16_t right = clampi(speedNow - steerNow, -1000, 1000);
    if (invertRight) right = -right;
    if (sendLeft) sendSpeed(ID_LEFT, left);
    else sendSpeed(ID_RIGHT, right);
    sendLeft = !sendLeft;
  }

  if (now - lastPrint >= 500) {
    lastPrint = now;
    for (int i = 0; i < 2; i++) {
      bool alive = fb[i].lastMs && (now - fb[i].lastMs < 300);
      Serial.printf("%s %-5s %6.2f km/h %5.2f V odom %7ld  ok %lu bad %lu | ",
                    i == 0 ? "L" : "R", alive ? "ok" : "NO-RX", fb[i].kmh, fb[i].volts,
                    (long)fb[i].odom, (unsigned long)fb[i].good, (unsigned long)fb[i].bad);
    }
    Serial.printf("cmd speed %d steer %d\n", speedNow, steerNow);
  }
}
