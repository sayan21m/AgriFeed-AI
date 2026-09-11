# AgriFeed-AI

**Project report · Smart India Hackathon 2026 · College internal round**

| | |
|---|---|
| Problem statement | **SIH26111** |
| Title | Rapid, low-cost, portable digital kit for cattle feed and silage quality |
| Ministry | Fisheries, Animal Husbandry & Dairying |
| Category | Software (with a village hardware kit) |
| Product | **AgriFeed-AI** bilingual farmer app (on-device scoring) + ESP32 measurement board |
| Date | September 2026 |

---

## 1. Abstract

Indian dairy farmers buy oilcakes, bran, compounded feed and silage with almost no village-level test. Adulteration (urea, sand), high moisture, poor fermentation and mould are common, but a mill NIR lab is too slow and too expensive for a bag bought at the mandi.

**AgriFeed-AI** is a five-minute kit. The farmer names the feed (English or Hindi aliases such as *sarson khali*). The ESP32 **only measures** moisture, optional silage pH and an 18-band AS7265x colour chip. AgriFeed-AI holds the tables, takes the mould photo, converts % dry matter to as-fed, screens urea and sand, scores silage with the Flieg formula, and speaks **Feed / Dilute / Reject** (खिलाएँ / मिलाकर खिलाएँ / न खिलाएँ).

The design is deliberately honest. Moisture is not protein. Phone RGB is not NIR. The AS7265x (410–940 nm) is recorded but **refused for crude-protein scoring** because protein N–H overtones sit near 1510–2180 nm and no Indian paired calibration exists for this chip. Aflatoxin is a historical risk table, not µg/kg. A public Brazilian forage NIR set is used only to show that real spectra *can* beat a name model — not as a claim on Indian oilcake or silage.

---

## 2. Problem (as issued)

Dairy animals in India are fed crop residues, oilseed cakes, bran, compounded cattle feed and silage. Quality varies by season, storage and adulteration. The problem statement asks for a **rapid, low-cost, portable, multilingual, offline-capable** digital method to test **feed and silage** for:

- nutritive value (especially crude protein),
- moisture,
- fermentation quality of silage,
- urea and sand / silica adulteration,
- mould / aflatoxin risk.

A FOSS or Bruker mill NIR is the industry gold standard. It is not a village kit. The gap is a tool a union secretary or a literate farmer can run in five minutes without claiming laboratory decimals they do not have.

---

## 3. Objectives

1. Return **Indian table ranges** (NDDB, BIS, ICAR papers) for known ingredients, not a fake single lab value from a photo.
2. Fuse **sensors that actually measure something** (moisture, pH, 4-DMAB yellow area, AIA / jar grit, a mould photo) into one farmer action.
3. Speak the result in **English and Hindi**.
4. Keep an ESP32 path for moisture, pH and AS7265x, with the **photo on the phone**.
5. Never map AS7265x, phone RGB or moisture onto crude protein or aflatoxin ppb.

---

## 4. Proposed solution

```
AgriFeed-AI (Flutter, fully offline)
  name + photo + EN/HI UI + tables + Flieg/urea/sand/HSV
        ▲  optional /api/sensors
ESP32 hotspot SSID SmartFeed  (moisture · pH · 18× AS7265x log)
```

**What each input is allowed to do**

| Input | Role | Must not claim |
|---|---|---|
| Ingredient name | Lookup 77 Indian feeds; TF-IDF fallback if unknown | Lab CP of *this* bag |
| Moisture probe | Convert % DM → as-fed; flag wet compounded feed / wet silage | Protein |
| Pocket pH | Flieg score with dry matter | NIR fermentation |
| 4-DMAB yellow area | Ridge screen on Anitha 2022 (1–10 g/kg) | Kjeldahl urea |
| Phone photo / mould tick | HSV on AgriFeed-AI; CNN desk-only | AFB1 µg/kg |
| Settling jar / AIA % | Sand suspicion or BIS fail | NIR sand |
| Bag QR | Expiry + declared CP/moisture vs tables and probe | Cryptographic mill seal; this bag's lab CP |
| AS7265x 18 bands | Logged, then **refused** for CP | Indian oilcake protein |
| 256-band forage NIR | Demo model on Brazilian tropical forage only | Indian bags |

Verdicts are **feed < dilute < reject**. Every module may raise a trigger; the pipeline takes the **worst**, so rule order cannot soften a reject. Milder flags stay under `other_flags`.

---

## 5. System architecture

### 5.1 Software

| Path | Function |
|---|---|
| `smartfeed/` | Models, validation, fusion, spoken paragraph |
| `app/` | FastAPI backend, kit ingest, model pack |
| `mobile/` | **AgriFeed-AI** Flutter app (on-device tables + rules, EN/HI, camera, TTS, logo) |
| `models/` | Runtime ExtraTrees / Ridge / CNN / PLS pack (replace + reload) |
| `firmware/esp32/` | ESP32 measurement sketch (no models on the MCU) |
| `notebooks/` | One notebook per module, with `artifacts/metrics.json` |
| `data/processed/` | Machine-readable tables from NDDB / BIS / ICAR papers |
| `tests/` | pytest cases (pipeline + HTTP) |

Main API:

- `GET /api/health`
- `GET /api/ingredients` — 77 canonical names
- `POST /api/kit` — ESP32 telemetry
- `GET /api/kit` — last kit reading for the phone
- `POST /api/assess` — name + sensors + optional photo → decision + `spoken`
- `GET /api/models` — on-disk model pack (version, sizes, hashes)
- `GET /api/models/files/{id}` — download one weight file
- `POST /api/models/reload` — reread `models/` after a replacement

CLI: `python3 -m smartfeed "mustard cake" --moisture 10 --lang hi`

### 5.2 Hardware (village kit)

**Offline mode (what we take to the field):** AgriFeed-AI already holds the 77 Indian ingredient ranges, aliases, Flieg, 4-DMAB slopes and sand/BIS rules. The ESP32 opens a Wi-Fi hotspot named `SmartFeed` and only serves `GET /api/sensors` (moisture, pH, 18 AS7265x bands). There is no laptop, no internet, and **no model on the MCU**.

Unknown names on the phone fall back to a keyword class and that class’s CP range. ExtraTrees / 256-band PLS stay in notebooks. AS7265x is refused for crude protein. Mould is a phone tick or HSV photo: the ESP32 does not decode a JPEG.

| Part | ESP32 pin | Notes |
|---|---|---|
| Capacitive moisture | GPIO 34 | Calibrate dry / wet raw counts |
| Analog pH (silage) | GPIO 35 | Optional; pH 4 and 7 buffers |
| AS7265x triad (51+52+53) | I2C 21 / 22, addr `0x49` | 18 bands logged, not scored as CP |
| Farmer phone | AgriFeed-AI joins `SmartFeed` AP | Scoring + screen + speaker + logo |

Without a board, `python3 firmware/simulate_kit.py --moisture 10` posts the same JSON.

### 5.3 Farmer flow

1. Open **AgriFeed-AI**. Tables are already on the phone. Optional: switch the board on and tap **Connect** (the app joins Wi-Fi `SmartFeed`).
2. Name the feed (`sarson khali`, mustard cake, maize silage, …), or scan the bag QR on **Verify Bag**.
3. **Connect** fills moisture / pH, or type them. A scanned QR can prefill the name and declared moisture.
4. Take a photo on the phone if mould is possible.
5. **Test now** → stamp **Feed / Dilute / Reject**. Expired QR or a CP/moisture mismatch **dilutes**. **Hear advice** uses `en-IN` / `hi-IN`.

---

## 6. Data sources

Public Indian sources are **reference tables and paper summaries**, not a national bag-level CSV. That is why known names return a **min–max range**.

| Source | Use in AgriFeed-AI |
|---|---|
| NDDB *Nutritive Value of Commonly Available Feeds and Fodders in India* (2012) | Concentrate and roughage lookup |
| BIS **IS 2052:2023** compounded cattle feed | Moisture ≤ 11%; CP ≥ 22 / 20% DM (Type I / II); AIA ≤ 2.5 / 3.0%; urea ≤ 1% DM; AFB1 ≤ 20 µg/kg |
| BIS IS 2052:2009 Annex C | Typical ingredient composition |
| Dey 2014 (Bihar), Singh 2016, Kannan 2017 | Extra Indian composition rows |
| Kaur et al. 2026, Punjab farmer silage (n = 100 **summary**) | Silage pH / Flieg context |
| Hundal 2020 wheat silage; Brar 2021 maize cultivar silage | Experimental silage rows |
| Anitha 2022, ARCC | Foldscope 4-DMAB yellow area vs urea g/kg on three cakes |
| Kotinagu 2015, *Veterinary World* | AFB1 **incidence** in AP / Telangana feeds — not this-bag ppb |
| Marcondes 2025, Figshare 28734674 (CC BY 4.0) | 291 Brazilian tropical forages, 256 NIR bands (890–1707 nm) + wet-lab CP/NDF/ADF. **Demo only.** |

Harvard Dataverse CIAT *Urochloa* NIR (guestbook-gated) was **not** used.

---

## 7. Models and performance

Cross-validation is **leave-one-ingredient-out** for names and **leave-one-species-out** for NIR, not a shuffled split that leaks the same species into train and test.

### 7.1 Nutrition from the typed name

- **77** canonical ingredients, **133** training rows after aliasing (`dorb` → deoiled rice bran, `gnc` → groundnut cake, `binola khali` → cottonseed cake, …).
- Exact table hit → fuzzy match (cutoff 0.82) → on the phone, a **keyword class** + class CP range. ExtraTrees + TF-IDF remains the desk/notebook fallback.
- Feed-class classifier: **ExtraTrees + char/word TF-IDF**, leave-one-ingredient-out accuracy **79.6%**.
- Crude protein regressor: **Ridge + TF-IDF**, CP MAE **5.11 % DM** (n = 108). An MLP lost to Ridge on the same protocol and is not shipped.
- Known feeds still show the table **range** (example: mustard cake CP 30.8–38.0% DM, mean 34.94%). The name model only fills unknown names.

Moisture conversion (does not measure protein):

```
as_fed = value_%DM × (1 − moisture/100)
```

Compounded feed moisture above **11%** is a dilute trigger (BIS).

### 7.2 Silage (Flieg)

```
Flieg = 220 + (2 × DM% − 15) − 40 × pH
```

| Score | Class | Farmer action |
|---|---|---|
| ≥ 81 | very good | Feed |
| 61–80 | good | Feed |
| 41–60 | satisfactory | Context only |
| 21–40 | moderate | Dilute |
| ≤ 20 | poor | Reject |

A pit with **pH > 4.2 and DM < 30%** is diluted even if Flieg still reads “satisfactory”, because that flag means the mass never soured properly. Kaur’s Punjab n = 100 figure (median pH 3.99, Flieg 104) is **summary context**, not raw pit rows.

### 7.3 Urea (4-DMAB)

Ridge per oilcake on Anitha 2022 (9 points: soybean meal, groundnut cake, undecorticated cottonseed cake × 1 / 5 / 10 g/kg). Calibration yellow-area is roughly **6.7–67%**. Above the top of the curve the result is a **lower bound**, not a straight-line guess of 15 g/kg. BIS max **1% DM** if urea is declared. In-sample MAE on those 9 points is ~0.02 g/kg; that number is **not** a field accuracy claim.

### 7.4 Aflatoxin risk

Kotinagu 2015 incidence lookup (cattle feed, maize, groundnut cake, cotton seed cake, soyabean cake, brans). **Does not predict ppb.** High-risk ingredient **plus** mould → reject. `maize silage` does **not** inherit maize-grain incidence (different matrix).

### 7.5 Visible mould (CV)

There is **no Indian feed-bag image dataset** (`public_feed_bag_images: 0`). GrainSet-tiny was skipped.

A **CNN** was trained on 1,920 synthetic 32×32 patches: clean cake, clean bran, **uniform green silage**, and mould blotches on brown. Held-out n = 480:

| Model | Accuracy | Note |
|---|---|---|
| CNN (desk / notebook only) | **1.00** | On this synthetic split; **not** in AgriFeed-AI |
| HSV colour screen | 0.54 | High recall, false-flags green fodder |

AgriFeed-AI uses the HSV screen plus the farmer checkbox. The CNN is not in the APK. **Not AFB1 µg/kg. Not real bag photos.** The 1.00 figure will not hold on dusty mandi lighting until we have labelled Indian bags.

### 7.6 Sand / silica

- Measured **acid-insoluble ash %** vs BIS 2.5% (Type I) / 3.0% (Type II) can **reject**.
- Village **settling-jar** (ml grit per 100 g) can only **suspect**. A jar test never proves a BIS fail.

### 7.7 NIR (Brazilian forage demo)

Marcondes 2025: **291** samples, **256** bands, 890–1707 nm. Pre-treatment: SNV; Savitzky–Golay 1st derivative (window 11, poly 2) when the winner name contains SG1.

| Analyte | Winner | Leave-one-species-out MAE | LOGOS R² |
|---|---|---|---|
| CP % DM | PLS 8 latent vars + SNV + SG1 | **1.39** | 0.75 |
| NDF % DM | PLS 8 + SNV | 3.79 | 0.50 |
| ADF % DM | PLS 8 + SNV | 2.56 | 0.61 |

Shuffled K-fold CP MAE (1.20) is **optimistic** and is not the number we quote. This calibration is **invalid** on Indian mustard cake, DORB, silage or compounded feed. **18 AS7265x channels are rejected** (`used: false`).

### 7.8 Ration note

Not a formulated TMR. A lactating crossbred ration is typically **12–16% CP DM**. Wheat straw at ~3.3% CP is still “feed” as roughage, with an explicit warning that it cannot be the whole diet.

### 7.9 Bag QR (SIH “QR-based authenticity”)

A mill or union can print a URL-safe base64 JSON payload: manufacturer, batch, pack/expiry dates, declared CP % DM, declared moisture, optional BIS licence and ingredient name. AgriFeed-AI scans it on **Verify Bag**, prefills the test, and compares:

- expiry vs today → **dilute** if past date;
- declared CP vs NDDB/BIS table mean → **dilute** if more than 5 percentage points apart;
- declared moisture vs the probe → **dilute** if more than 3 points apart.

The prototype is **unsigned**. A production union would sign the payload. This is not a lab certificate for the bag in the farmer’s hand.

---

## 8. Decision examples

| Input | Action | Why |
|---|---|---|
| Mustard cake, moisture 10% | **Feed** | Table CP ~31–38% DM; no flags |
| Wheat straw, moisture 9% | **Feed** + ration warning | ~3.3% CP; filler roughage only |
| Cattle feed, moisture 16%, form compounded | **Dilute** | Above BIS 11% moisture |
| Groundnut cake + mould | **Reject** | Visible mould + high-AF-risk ingredient |
| Cattle feed, AIA 4% | **Reject** | Sand / silica over BIS |
| Mustard cake, 4 ml grit / 100 g | **Dilute** | Jar test suspects sand; does not prove AIA |
| Mustard cake + expired bag QR | **Dilute** | QR expiry date is past |
| Mustard cake + QR declaring 12% CP | **Dilute** | Declared CP more than 5 points from the table |
| Maize silage, pH 5.2, moisture 78% | **Dilute** | High pH on low DM + too wet |
| 18 AS7265x counts on wheat bran | Feed (if nothing else) | Chip **not used** for CP |

Impossible readings (moisture 150%, pH 99) raise `SensorRangeError` instead of printing **−17% protein**.

---

## 9. Implementation notes

- Python 3.10+, FastAPI, scikit-learn ≥ 1.8 (joblib artifacts pickled with 1.8.x), scipy, Pillow.
- Runtime weights sit in `models/` (~3 MB). Notebooks stay the training source. `POST /api/models/reload` drops RAM caches after a file swap.
- The farmer UI is **AgriFeed-AI** (`mobile/`). Home-screen name and mark: `mobile/assets/images/logo.png`. Scoring runs **on the phone** (bundled `offline_kit.json` + the same feed/dilute/reject rules). ExtraTrees / CNN / PLS stay in notebooks and the optional desk FastAPI.
- Photo mould on the phone is HSV. The synthetic CNN is not shipped in the APK.
- Spoken text is assembled from the verdict, CP range, moisture conversion, Flieg, mould, and an explicit sentence when 18 bands were ignored.
- Offline intent of the PS: the APK scores without a laptop or internet. The ESP32 is optional and measurement-only.

Tests: `python3 -m pytest -q` → **29 passed**.

---

## 10. What we will not claim to judges

- We did **not** train a national Indian NIR crude-protein model.
- We did **not** clone FOSS / Bruker.
- We do **not** read protein from moisture, from a phone photo, or from AS7265x.
- We do **not** output aflatoxin ppb.
- An MLP lost to ExtraTrees / Ridge (names) and to PLS (NIR); those nets are not shipped.
- NDDB / BIS numbers are **typical composition**, not this-bag wet chemistry.
- The 4-DMAB curve must not be extrapolated past 10 g/kg as if it were linear.

Honesty is part of the product. A village kit that invents 0.1% CP from a ₹400 colour chip would be more dangerous than no kit.

---

## 11. Cost and portability (indicative)

| Item | Role | Indicative |
|---|---|---|
| ESP32 DevKit | MCU + Wi-Fi | ~₹400 |
| Capacitive moisture probe | % moisture | ~₹150–300 |
| Analog pH probe | Silage only | ~₹400–800 |
| AS7265x triad | 18-band colour log | chip ~$4; breakout higher |
| 4-DMAB paper | Urea screen | cents / strip |
| Farmer phone | Photo + UI + TTS | already owned |

No mill NIR, no wet-lab Kjeldahl on site. Union lab remains the referee for AFB1 and AIA.

---

## 12. Future work (if selected beyond college internal)

1. Pair **Indian** oilcake / DORB / silage bags with wet-lab CP and a spectrometer that actually covers ~1500–2200 nm.
2. Lateral-flow AFB1 strip as a true ppb screen; keep the photo as mould-only.
3. Calibrate the capacitive probe on the actual feed matrices (cake vs silage vs bran).
4. Port ExtraTrees / the synthetic CNN onto the phone if a later trial needs unknown-name guesses beyond the keyword class.
5. Field trial with one milk union: agreement vs lab on moisture and Flieg, not vs imagined NIR CP.

---

## 13. How to run (internal demo)

```bash
python3 -m pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# optional, no ESP32:
python3 firmware/simulate_kit.py --moisture 10
```

Open `http://127.0.0.1:8000` for a desk browser demo, or run AgriFeed-AI:

```bash
cd mobile && flutter run
```

Demo path (no laptop): mustard cake → Test now → Hear advice; then groundnut cake + mould → Reject. Optional ESP32: power the board, tap **Connect**.

ESP32 flash instructions: `firmware/esp32/README.md`.

---

## 14. References (used)

1. NDDB (2012). *Nutritive Value of Commonly Available Feeds and Fodders in India.*
2. Bureau of Indian Standards. IS 2052:2023 *Compounded Feeds for Cattle — Specification.*
3. Bureau of Indian Standards. IS 2052:2009, Annex C (typical ingredient composition).
4. Dey, A. et al. (2014). Feed composition, Bihar. *Indian Journal of Animal Sciences.*
5. Singh, S. et al. (2016). Energy and protein feeds. *Indian Journal of Animal Sciences.*
6. Kannan, A. et al. (2017). NW Himalayan concentrates. *Indian Journal of Animal Sciences.*
7. Kaur et al. (2026). Punjab farmer silage, n = 100 summary. *Indian Journal of Dairy Science.*
8. Hundal, J.S. et al. (2020). Wheat silage. *Indian Journal of Animal Sciences.*
9. Brar, N.S. et al. (2021). Maize cultivar silage. *Indian Journal of Agricultural Sciences.*
10. Anitha, N. et al. (2022). Foldscope yellow area vs urea in oilseed cakes. ARCC.
11. Kotinagu, K. et al. (2015). AFB1 in feeds, Andhra Pradesh / Telangana. *Veterinary World.*
12. Marcondes, M.I. et al. (2025). Tropical forage NIR + chemistry. Figshare. https://doi.org/10.6084/m9.figshare.28734674
13. Flieg score as used in Indian silage papers: \(220 + (2 \times \mathrm{DM\%} - 15) - 40 \times \mathrm{pH}\).

---

## 15. One-page summary for the jury

**Problem.** Village dairy farmers cannot test the bag or the pit in five minutes.

**What we built.** AgriFeed-AI + an ESP32 kit that looks up Indian tables, reads moisture and pH, screens urea / sand / mould, and **says** feed, mix, or reject.

**Numbers we stand behind.** 77 ingredients; name-model CP MAE **5.11% DM**; class accuracy **79.6%**; Brazilian forage NIR CP MAE **1.39% DM** (leave-one-species-out); 29 automated tests.

**Numbers we refuse.** Camera → CP. AS7265x → Indian CP. Moisture → protein. Photo → aflatoxin ppb.

**Ask.** A field pairing of Indian bags with a real NIR range, not a prettier dashboard.
