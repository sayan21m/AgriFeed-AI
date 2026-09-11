const I18N = {
  en: {
    kicker: "SIH26111 · DAHD",
    title: "SmartFeed",
    ingredient: "What is this feed?",
    form: "Form",
    form_ing: "Ingredient",
    form_sil: "Silage",
    form_cmp: "Compounded",
    moisture: "Moisture %",
    ph: "Silage pH",
    urea: "4-DMAB yellow %",
    mould: "Visible mould",
    photo: "Phone photo (mould)",
    test: "Test now",
    testing: "Testing…",
    cp: "Crude protein % DM",
    asfed: "CP as-fed %",
    method: "Method",
    flieg: "Flieg score",
    moisture_dm: "Dry matter %",
    urea_est: "Urea g/kg (screen)",
    af: "AFB1 risk (historical)",
    why: "Why",
    none: "—",
    sand: "Sand / silica",
    grit: "Settled grit (ml)",
    sample_g: "Sample weight (g)",
    aia: "AIA % (if lab tested)",
    ration: "How to use it today",
    also: "Also noted",
    sensor: "Check your sensors",
    kit: "ESP32 kit",
    kit_idle: "No reading yet. Power the board or simulate.",
    kit_pull: "Use kit",
    kit_ok: "Kit {id} · moisture {m}%{ph}{chip}",
    kit_chip: " · 18 colour bands (not protein)",
    kit_none: "No kit reading on the server yet.",
    hear: "Hear advice",
    chip: "Colour chip",
    tab_test: "Test",
    tab_result: "Verdict",
    tab_models: "Models",
    result_empty: "Run a test. The verdict will show here.",
    models_lead: "Weights live in the models/ pack on disk — not inside a web page. Replace a file and tap Update.",
    models_update: "Update & reload",
    models_updating: "Updating…",
    models_done: "Pack reloaded. Next test uses the new files.",
    install: "Install the app on this phone so the model pack can sit on disk.",
    install_btn: "Add",
  },
  hi: {
    kicker: "SIH26111 · पशुपालन विभाग",
    title: "स्मार्टफीड",
    ingredient: "यह चारा क्या है?",
    form: "प्रकार",
    form_ing: "कच्चा चारा",
    form_sil: "साइलेज",
    form_cmp: "मिश्रित दाना",
    moisture: "नमी %",
    ph: "साइलेज pH",
    urea: "4-DMAB पीला %",
    mould: "दिखने वाली फफूंद",
    photo: "फोन फोटो (फफूंद)",
    test: "अभी जाँचें",
    testing: "जाँच हो रही है…",
    cp: "क्रूड प्रोटीन % DM",
    asfed: "CP जैसा खिलाया %",
    method: "विधि",
    flieg: "Flieg अंक",
    moisture_dm: "शुष्क पदार्थ %",
    urea_est: "यूरिया ग्रा/किग्रा (स्क्रीन)",
    af: "AFB1 जोखिम (पुराना आँकड़ा)",
    why: "कारण",
    none: "—",
    sand: "रेत / सिलिका",
    grit: "बैठी हुई रेत (मिली)",
    sample_g: "नमूने का वज़न (ग्राम)",
    aia: "AIA % (यदि लैब जाँच हुई हो)",
    ration: "आज इसका उपयोग कैसे करें",
    also: "यह भी ध्यान दें",
    sensor: "सेंसर जाँचें",
    kit: "ESP32 किट",
    kit_idle: "अभी कोई रीडिंग नहीं। बोर्ड चलाएँ या सिम्युलेट करें।",
    kit_pull: "किट लें",
    kit_ok: "किट {id} · नमी {m}%{ph}{chip}",
    kit_chip: " · 18 रंग बैंड (प्रोटीन नहीं)",
    kit_none: "सर्वर पर किट रीडिंग नहीं है।",
    hear: "सलाह सुनें",
    chip: "रंग चिप",
    tab_test: "जाँच",
    tab_result: "फैसला",
    tab_models: "मॉडल",
    result_empty: "जाँच चलाएँ। फैसला यहाँ दिखेगा।",
    models_lead: "वेट models/ फ़ोल्डर में हैं, वेब पेज में नहीं। फ़ाइल बदलें और अपडेट दबाएँ।",
    models_update: "अपडेट और रीलोड",
    models_updating: "अपडेट हो रहा है…",
    models_done: "पैक रीलोड हुआ। अगली जाँच नई फ़ाइलें इस्तेमाल करेगी।",
    install: "ऐप फ़ोन पर इंस्टॉल करें ताकि मॉडल डिस्क पर रह सकें।",
    install_btn: "जोड़ें",
  },
};

let lang = "en";
let lastSpoken = { en: "", hi: "" };
let kitSpectrum = null;
let deferredInstall = null;

function t(key) {
  return I18N[lang][key] || key;
}

function applyLang() {
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  document.getElementById("lang-en").classList.toggle("on", lang === "en");
  document.getElementById("lang-hi").classList.toggle("on", lang === "hi");
  const spoken = document.getElementById("spoken-text");
  if (spoken && (lastSpoken.en || lastSpoken.hi)) {
    spoken.textContent = lastSpoken[lang] || lastSpoken.en;
  }
}

function showScreen(name) {
  document.querySelectorAll(".screen").forEach((el) => {
    el.classList.toggle("hidden", el.id !== `screen-${name}`);
  });
  document.querySelectorAll(".tab").forEach((el) => {
    el.classList.toggle("on", el.dataset.screen === name);
  });
  if (name === "models") loadModels().catch(() => {});
}

function num(v) {
  if (v === null || v === undefined || v === "") return "";
  const n = Number(v);
  return Number.isFinite(n) ? n : "";
}

function spanText(span) {
  if (!span) return t("none");
  if (span.min != null && span.max != null) return `${span.mean}  (${span.min}–${span.max})`;
  return String(span.mean ?? t("none"));
}

function speakAdvice() {
  const text = lastSpoken[lang] || lastSpoken.en;
  if (!text || !window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = lang === "hi" ? "hi-IN" : "en-IN";
  window.speechSynthesis.speak(u);
}

function kb(bytes) {
  if (bytes > 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${Math.round(bytes / 1024)} KB`;
}

function render(data) {
  const farmer = data.farmer || {};
  const nut = data.modules.nutrition || {};
  const moist = data.modules.moisture || {};
  const silage = data.modules.silage || {};
  const urea = data.modules.urea || {};
  const af = data.modules.aflatoxin || {};
  const nir = data.modules.nir || {};
  const action = farmer.action || "feed";
  const label = lang === "hi" ? farmer.label_hi : farmer.label_en;
  const summary = lang === "hi" ? farmer.summary_hi : farmer.summary_en;
  const reasons = lang === "hi" ? farmer.reasons_hi : farmer.reasons_en;
  const other = (lang === "hi" ? farmer.other_flags_hi : farmer.other_flags_en) || [];
  const ration = data.ration || {};
  const tips = (lang === "hi" ? ration.tips_hi : ration.tips_en) || [];
  const role = lang === "hi" ? ration.role_hi : ration.role_en;
  const warns = data.sensor_warnings || [];
  const cp = (nut.nutrients_pct_dm || {}).crude_protein_pct_dm;
  const asfed = (nut.nutrients_as_fed || {}).crude_protein_pct;
  lastSpoken = data.spoken || { en: summary || "", hi: farmer.summary_hi || "" };
  const spoken = lastSpoken[lang] || lastSpoken.en || "";
  const chipNote = nir.used === false
    ? (lang === "hi" ? "18 बैंड आए, प्रोटीन नहीं निकाला" : "18 bands received, not used for protein")
    : (nir.used ? (lang === "hi" ? "256-बैंड चारा NIR (ब्राज़ील)" : "256-band forage NIR (Brazil only)") : t("none"));
  document.getElementById("result-empty").classList.add("hidden");
  const box = document.getElementById("result");
  box.classList.remove("hidden");
  box.innerHTML = `
    <div class="stamp ${action}">
      <h2>${label || action}</h2>
      <p>${summary || ""}</p>
    </div>
    <p id="spoken-text" class="spoken">${spoken}</p>
    <button type="button" id="hear" class="ghost hear">${t("hear")}</button>
    <div class="metrics">
      <div class="metric"><span>${t("cp")}</span><b>${spanText(cp)}</b></div>
      <div class="metric"><span>${t("asfed")}</span><b>${spanText(asfed)}</b></div>
      <div class="metric"><span>${t("method")}</span><b>${nut.method || t("none")}</b></div>
      <div class="metric"><span>${t("moisture_dm")}</span><b>${moist.dry_matter_pct ?? t("none")}</b></div>
      <div class="metric"><span>${t("flieg")}</span><b>${silage.flieg_score ?? t("none")}</b></div>
      <div class="metric"><span>${t("urea_est")}</span><b>${urea.urea_g_per_kg ?? t("none")}</b></div>
      <div class="metric"><span>${t("chip")}</span><b>${chipNote}</b></div>
    </div>
    <p><strong>${t("why")}</strong></p>
    <ul>${(reasons || []).map((r) => `<li>${r}</li>`).join("")}</ul>
    ${other.length ? `<p><strong>${t("also")}</strong></p><ul>${other.map((r) => `<li>${r}</li>`).join("")}</ul>` : ""}
    ${tips.length ? `<p><strong>${t("ration")}</strong>${role ? ` — ${role}` : ""}</p><ul>${tips.map((r) => `<li>${r}</li>`).join("")}</ul>` : ""}
    ${warns.length ? `<p class="warn"><strong>${t("sensor")}</strong></p><ul class="warn">${warns.map((r) => `<li>${r}</li>`).join("")}</ul>` : ""}
    <p class="note">${t("af")}: ${af.high_risk_ingredient ? (lang === "hi" ? "ऊँचा" : "higher") : (lang === "hi" ? "कम / अज्ञात" : "lower / unknown")}
      ${af.matched_item ? ` · ${af.matched_item}` : ""}</p>
    <p class="note">${data.disclaimer || ""}</p>
  `;
  document.getElementById("hear").onclick = speakAdvice;
  showScreen("result");
}

function applyKit(reading) {
  const status = document.getElementById("kit-status");
  if (!reading) {
    status.textContent = t("kit_none");
    return;
  }
  if (reading.moisture_pct != null) document.getElementById("moisture").value = reading.moisture_pct;
  if (reading.ph != null) document.getElementById("ph").value = reading.ph;
  kitSpectrum = Array.isArray(reading.as7265x) ? reading.as7265x : null;
  const phBit = reading.ph != null ? ` · pH ${reading.ph}` : "";
  const chipBit = kitSpectrum ? t("kit_chip") : "";
  status.textContent = t("kit_ok")
    .replace("{id}", reading.device_id || "kit")
    .replace("{m}", reading.moisture_pct ?? "—")
    .replace("{ph}", phBit)
    .replace("{chip}", chipBit);
}

async function pullKit() {
  const res = await fetch("/api/kit");
  const data = await res.json();
  applyKit(data.reading);
}

async function loadIngredients() {
  const res = await fetch("/api/ingredients");
  const data = await res.json();
  const list = document.getElementById("ingredient-list");
  list.innerHTML = data.items.map((it) => `<option value="${it.canonical}"></option>`).join("");
}

async function loadModels() {
  const res = await fetch("/api/models");
  const pack = await res.json();
  document.getElementById("models-meta").textContent =
    `v${pack.version} · ${pack.files.length} files · ${kb(pack.total_bytes)} · ${pack.updated || ""}`;
  document.getElementById("models-list").innerHTML = (pack.files || []).map((f) => `
    <li>
      <strong>${f.file}</strong>
      <span>${f.role} · ${kb(f.bytes)} · ${f.sha256_16}</span>
    </li>
  `).join("");
}

async function updateModels() {
  const btn = document.getElementById("models-update");
  const status = document.getElementById("models-status");
  btn.disabled = true;
  btn.textContent = t("models_updating");
  status.textContent = "";
  try {
    const pack = await (await fetch("/api/models")).json();
    const cache = "caches" in window ? await caches.open("smartfeed-models") : null;
    for (const file of pack.files || []) {
      const res = await fetch(`/api/models/files/${file.id}`);
      if (!res.ok) throw new Error(`Could not fetch ${file.file}`);
      if (cache) await cache.put(`/models/${file.file}`, res.clone());
    }
    const reload = await fetch("/api/models/reload", { method: "POST" });
    if (!reload.ok) throw new Error(await reload.text());
    await loadModels();
    status.textContent = t("models_done");
  } catch (err) {
    status.textContent = err.message;
  } finally {
    btn.disabled = false;
    btn.textContent = t("models_update");
  }
}

document.getElementById("lang-en").onclick = () => { lang = "en"; applyLang(); };
document.getElementById("lang-hi").onclick = () => { lang = "hi"; applyLang(); };
document.getElementById("kit-pull").onclick = () => pullKit().catch((err) => {
  document.getElementById("kit-status").textContent = err.message;
});
document.getElementById("models-update").onclick = () => updateModels();
document.querySelectorAll(".tab").forEach((btn) => {
  btn.onclick = () => showScreen(btn.dataset.screen);
});

document.getElementById("photo").addEventListener("change", (ev) => {
  const file = ev.target.files[0];
  const img = document.getElementById("photo-preview");
  if (!file) {
    img.classList.add("hidden");
    img.removeAttribute("src");
    return;
  }
  img.src = URL.createObjectURL(file);
  img.classList.remove("hidden");
});

document.getElementById("kit").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const btn = ev.target.querySelector("button[type=submit]");
  btn.disabled = true;
  btn.textContent = t("testing");
  const fd = new FormData();
  fd.append("ingredient", document.getElementById("ingredient").value);
  fd.append("form", document.querySelector("input[name=form]:checked").value);
  const moisture = num(document.getElementById("moisture").value);
  const ph = num(document.getElementById("ph").value);
  const urea = num(document.getElementById("urea").value);
  if (moisture !== "") fd.append("moisture_pct", moisture);
  if (ph !== "") fd.append("ph", ph);
  if (urea !== "") fd.append("urea_yellow_area_pct", urea);
  for (const [id, field] of [["grit", "grit_settled_ml"], ["sample_g", "sample_g"], ["aia", "aia_pct"]]) {
    const v = num(document.getElementById(id).value);
    if (v !== "") fd.append(field, v);
  }
  fd.append("visible_mould", document.getElementById("mould").checked);
  if (kitSpectrum) fd.append("nir_json", JSON.stringify(kitSpectrum));
  const photo = document.getElementById("photo").files[0];
  if (photo) fd.append("photo", photo);
  try {
    const res = await fetch("/api/assess", { method: "POST", body: fd });
    if (!res.ok) throw new Error(await res.text());
    render(await res.json());
  } catch (err) {
    document.getElementById("result-empty").classList.add("hidden");
    const box = document.getElementById("result");
    box.classList.remove("hidden");
    box.innerHTML = `<p>${err.message}</p>`;
    showScreen("result");
  } finally {
    btn.disabled = false;
    btn.textContent = t("test");
  }
});

window.addEventListener("beforeinstallprompt", (ev) => {
  ev.preventDefault();
  deferredInstall = ev;
  document.getElementById("install-bar").classList.remove("hidden");
});
document.getElementById("install-btn").onclick = async () => {
  if (!deferredInstall) return;
  deferredInstall.prompt();
  await deferredInstall.userChoice;
  deferredInstall = null;
  document.getElementById("install-bar").classList.add("hidden");
};

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js").catch(() => {});
}

applyLang();
loadIngredients().catch(() => {});
pullKit().catch(() => {});
