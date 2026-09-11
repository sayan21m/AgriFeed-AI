# SmartFeed Flutter app

Farmer phone app for SIH26111. **Scoring runs on the phone.** 77 Indian feed tables, Flieg, 4-DMAB, sand/BIS, AF risk and HSV mould are bundled. No laptop server.

```bash
cd mobile
flutter pub get
flutter run
```

Type moisture / pH, or switch the board on and tap **Connect**. The app joins Wi-Fi **SmartFeed** and fills moisture / pH. No IP and no Settings app. The ESP32 only measures; it does not run tables or the verdict. English / हिंदी, camera photo, spoken verdict.

Unknown names use a **keyword class**, not ExtraTrees. Photo mould is the **HSV screen**, not the synthetic CNN. AS7265x 18 bands are refused for CP. Rebuild the pack after CSV changes:

```bash
python3 firmware/export_offline_tables.py
```
