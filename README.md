# AgriFeed-AI — SIH26111

Rapid, offline-friendly **cattle feed and silage** quality kit for Indian dairy farmers.  
Ministry of Fisheries, Animal Husbandry & Dairying · [problem statement](https://sih2026.vuce.in/ps/SIH26111)

The farmer app is **AgriFeed-AI** (logo on the home screen and in the top bar). This is **not** a FOSS mill NIR. Known feeds return Indian table **ranges**. Sensors convert units or screen adulteration. The app decides **feed / dilute / reject**.

## Run AgriFeed-AI (fully offline)

Scoring is **on the phone**. No laptop server.

```bash
cd mobile
flutter pub get
flutter run
```

English / हिंदी, camera photo, spoken verdict. Type moisture / pH, or switch the board on and tap **Connect** — AgriFeed-AI joins Wi-Fi **SmartFeed** (that is the board’s hotspot name). Unknown names use a keyword class (not ExtraTrees). Photo mould is HSV (not the synthetic CNN). AS7265x is refused for CP.

Rebuild the bundled tables after CSV changes:

```bash
python3 firmware/export_offline_tables.py
```

## ESP32 probe (measurement only)

The board **does not score**. Flash `firmware/esp32/smartfeed_kit/`, power it, then tap **Connect** in AgriFeed-AI. The app joins Wi-Fi **SmartFeed** and reads moisture, pH and 18 AS7265x bands from `GET /api/sensors`. Tables, Flieg, urea, sand and the verdict stay on the phone.

```bash
python3 firmware/export_offline_tables.py   # rebuild mobile/assets/offline_kit.json
```

Pinout: `firmware/esp32/README.md`.

The ExtraTrees name model and Brazilian NIR PLS stay in the notebooks. Unknown names on the phone use aliases + a keyword class.

Desk demo of the Python pipeline (notebooks / pytest), not required in the village:

```bash
python3 -m pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

A browser at http://127.0.0.1:8000 still works for a desk demo. The product UI is AgriFeed-AI.

Full write-up for the college internal round: [`docs/AgriFeed_AI_Project_Report.md`](docs/AgriFeed_AI_Project_Report.md).

## CLI

```bash
python3 -m smartfeed "mustard cake" --moisture 10
python3 -m smartfeed maize --form silage --moisture 70 --ph 3.9 --lang hi
python3 -m smartfeed "groundnut cake" --urea-yellow 62 --mould
python3 -m smartfeed "cattle feed" --form compounded --grit-ml 4 --sample-g 100
python3 -m smartfeed "wheat bran" --moisture 12 --json
```

Prints a farmer card by default (`--lang en|hi`); `--json` gives the full result.

## What each part does

| Path | Role |
|---|---|
| `mobile/` | **AgriFeed-AI** Flutter app — on-device tables + rules + logo |
| `mobile/assets/offline_kit.json` | 77 feeds, Flieg, urea, BIS, Kotinagu |
| `mobile/assets/images/logo.png` | AgriFeed-AI mark and launcher icon |
| `smartfeed/` | Models + fused `assess()` (Python / desk) |
| `app/` | FastAPI desk backend (optional) |
| `models/` | ExtraTrees / Ridge / CNN / PLS for notebooks + desk API |
| `firmware/esp32/` | ESP32 sketch: moisture, pH, AS7265x only |
| `notebooks/ml/` | Name → nutrition (79.6% class acc, CP MAE 5.11 % DM) |
| `notebooks/nir/` | Brazilian forage NIR demo — **not Indian bags** |
| `notebooks/cv/` | HSV + CNN mould screen (CNN is synthetic patches) |
| `data/processed/` | NDDB, BIS, ICAR paper tables |

## How the verdict is reached

Every module that has an input contributes a trigger of `feed`, `dilute`, or `reject`.
The pipeline takes the **worst** trigger, so rule order cannot soften a verdict; the
milder triggers are still reported under `other_flags`.

Readings outside physical range (moisture over 100%, pH over 14) raise
`SensorRangeError` instead of producing negative protein. Readings that are
possible but unusual come back in `sensor_warnings`.

## Honest limits

- Moisture does not measure protein.
- Phone RGB is not NIR.
- AS7265x (410–940 nm) is not calibrated here — 18 channels are refused for CP.
- Aflatoxin is a **risk table** (Kotinagu 2015), not µg/kg.
- NIR PLS (MAE 1.39 % DM) is Brazilian tropical forage only — not on the phone.
- The 4-DMAB curve was built on 1–10 g/kg urea. Above that the result is reported
  as a **lower bound**, not extrapolated.
- Photo mould **on the phone** is HSV (can false-flag green fodder). The CNN lives
  in the notebooks / desk API and was trained on **synthetic** patches, not Indian bags. Not aflatoxin ppb.
- Unknown names on the phone use a **keyword class**, not ExtraTrees.
- `ration` gives a role for one ingredient. It is not a balanced ration.

## Tests

```bash
python3 -m pytest -q
cd mobile && flutter test
```

Python: **29 tests** (pipeline + HTTP). The CNN-vs-HSV check needs the `torch` extra.
Flutter: widget smoke + on-device pipeline (same verdicts as Python for known feeds).

The joblib artifacts were pickled with scikit-learn 1.8.x. Installing an older
sklearn still loads them but warns that results may be invalid, so keep the
pinned floor in `requirements.txt`.
