# SmartFeed ESP32 — measurement probe

The board **only measures**. Moisture, optional silage pH and the AS7265x colour chip are read here. Tables, Flieg, urea, sand/BIS rules and the verdict live in the Flutter app (`mobile/assets/offline_kit.json`).

**AS7265x is still not crude protein.** ExtraTrees / 256-band PLS stay in the notebooks. The phone scores; this MCU does not.

## How a farmer uses it

1. Power the ESP32 (USB power bank is enough).
2. Open the **SmartFeed** Flutter app and tap **Connect**. The phone joins Wi-Fi **`SmartFeed`** and shows **Connected**. If the phone asks, tap Allow.
3. Type the feed name, tick mould if you see it, **Test now**. Hear the Hindi/English advice.

The optional page at the board only shows live sensor numbers. It does not score the bag.

No laptop. No internet. No `/api/assess` on the board.

## What is on the chip

| Piece | On ESP32? |
|---|---|
| Moisture / pH / AS7265x read + `GET /api/sensors` | Yes |
| 77 Indian ingredient ranges | **No** — phone (`offline_kit.json`) |
| Aliases + fuzzy name match | **No** — phone |
| Moisture → as-fed, BIS 11% | **No** — phone |
| Flieg from pH + DM | **No** — phone |
| 4-DMAB Ridge slopes | **No** — phone |
| Sand jar / AIA vs BIS | **No** — phone |
| AFB1 *risk* if mould + high-risk cake | **No** — phone |
| Spoken EN/HI paragraph | **No** — phone TTS |
| ExtraTrees + TF-IDF name model | **No** |
| Brazilian 256-band PLS | **No** |
| AS7265x → Indian CP | **No** (refused; 18 bands logged only) |

Rebuild the phone tables after changing CSVs:

```bash
python3 firmware/export_offline_tables.py
```

## Wiring (ESP32 Dev Module)

| Part | Pin |
|---|---|
| Capacitive moisture | GPIO 34 |
| Analog pH | GPIO 35 |
| AS7265x SDA/SCL | GPIO 21 / 22 |

## Flash

Arduino IDE → **ESP32 Dev Module**. Open `firmware/esp32/smartfeed_kit/smartfeed_kit.ino`. Copy `config.h.example` to `config.h` if needed. `OFFLINE_AP 1` is the field mode.

`GET /api/sensors` returns `moisture_pct`, `ph`, `as7265x` (18 floats or null), `models_on_board: false`, `as7265x_used_for_cp: false`.

## Laptop app

`python3 -m uvicorn app.main:app` is still useful on a desk for pytest and notebooks. In the village, score on the phone; use the ESP32 only for probes.
