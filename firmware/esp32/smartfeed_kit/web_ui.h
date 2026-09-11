#pragma once
#include <Arduino.h>

static const char INDEX_HTML[] PROGMEM = R"HTML(
<!DOCTYPE html>
<html lang="en">
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>SmartFeed probe</title>
<style>
body{font-family:Georgia,serif;background:#f4efe4;color:#101610;margin:0}
.top{background:#1b3a24;color:#fff8ec;padding:18px}
h1{margin:4px 0 8px;font-size:24px}
.card{background:#fffdf7;border:1px solid #d4cbb8;margin:14px;padding:16px}
.note{color:#334033;font-size:14px;line-height:1.4}
.ghost{padding:10px 14px;border:1px solid #1b3a24;background:#fff;font:inherit}
#st{font-size:18px;margin:0 0 12px}
</style>
<body>
<div class="top">
  <p class="note" style="color:#f6e9c8">SIH26111 · measurement only</p>
  <h1>SmartFeed probe</h1>
  <p>This board only measures moisture, pH and the colour chip. Open the <b>SmartFeed</b> phone app to score the feed. Models are not on the ESP32.</p>
</div>
<div class="card">
  <p id="st">Reading sensors…</p>
  <button class="ghost" type="button" id="pull">Refresh sensors</button>
  <p class="note" id="hint">Join Wi-Fi SmartFeed, then tap Use kit in the app.</p>
</div>
<script>
async function pull(){
  const d=await (await fetch('/api/sensors')).json();
  const n=d.as7265x&&d.as7265x.length?d.as7265x.length+' bands (not protein)':'off';
  document.getElementById('st').textContent='moisture '+(d.moisture_pct??'—')+'% · pH '+(d.ph??'—')+' · AS7265x '+n;
}
document.getElementById('pull').onclick=pull;
pull();
</script>
</body>
</html>
)HTML";
