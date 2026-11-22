# Flashing (Windows, Kevin only)

Flashing and bench tests happen only on Kevin's Windows PC, never on the OptiPlex or by Claude.

## Setup
- ST-Link **powers the board through its 3.3 V pin**. No battery and no bench supply connected.
- OpenOCD comes from PlatformIO: `<home>/.platformio/packages/tool-openocd`.
- **Use forward slashes** in every path passed to openocd (`C:/Users/<name>/.platformio/...`);
  backslashes get eaten by its Tcl parser.

## Settings that matter
| Setting | Value | Why |
|---|---|---|
| `adapter speed 200` | 200 (≈125 kHz actual) | the default speed fails with `init mode failed` |
| `-c "set CPUTAPID 0"` | before the target cfg | the GD32 TAP ID doesn't match the STM32 one |
| `-f target/stm32f1x.cfg` | | used for **both** boards |

Both boards (master GD32F103, slave GD32F130) report the same device id `0x13030410`, so the
id can't tell them apart. **Confirm which board is connected by the chip marking.**

## Command shape
```
openocd -s <openocd>/openocd/scripts -f interface/stlink.cfg \
  -c "set CPUTAPID 0" -f target/stm32f1x.cfg -c "adapter speed 200" \
  -c "init" -c "halt" ...
```
(`<openocd>` = `C:/Users/<name>/.platformio/packages/tool-openocd`; adjust the scripts path to
the package layout.)

## Verify
After any write, read the flash back and compare hashes:
```
... -c "dump_image readback.bin 0x08000000 <size>" -c "exit"
```
then hash `readback.bin` and the source `.bin` (`certutil -hashfile <file> SHA256`); they must match
(compare over the length of the source `.bin`).
Keep stock backups and readbacks out of git (see `.gitignore`).
