# AgriFeed-AI

Farmer phone app for SIH26111. Home-screen name **AgriFeed-AI**. Logo: `assets/images/logo.png` (top bar + launcher icon).

**Scoring runs on the phone.** 77 Indian feed tables, Flieg, 4-DMAB, sand/BIS, AF risk and HSV mould are bundled. No laptop server.

```bash
cd mobile
flutter pub get
flutter run
```

Type moisture / pH, or switch the board on and tap **Connect**. AgriFeed-AI joins Wi-Fi **SmartFeed** (ESP32 hotspot name) and fills moisture / pH. No IP and no Settings app. The ESP32 only measures; it does not run tables or the verdict. English / हिंदी, camera photo, spoken verdict.

**Verify Bag** scans a mill QR (manufacturer, batch, expiry, declared CP / moisture) and fuses it into the same feed / dilute / reject stamp. Demo QRs are on that tab for judges without a printed bag. The payload is unsigned prototype authenticity, not a mill cryptographic seal.

Unknown names use a **keyword class**, not ExtraTrees. Photo mould is the **HSV screen**, not the synthetic CNN. AS7265x 18 bands are refused for CP. Rebuild the pack after CSV changes:

```bash
python3 firmware/export_offline_tables.py
```

After changing the logo, regenerate launcher icons:

```bash
dart run flutter_launcher_icons
```
