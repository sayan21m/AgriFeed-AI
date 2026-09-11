// Purge old stale service worker cache so updates are immediately visible!
if ("caches" in window) {
  caches.delete("smartfeed-shell").catch(() => {});
}

const I18N = {
  en: {
    hero_title: "Rapid Cattle Feed & Silage Quality Assessment",
    hero_desc: "Portable digital testing powered by Indian dairy tables (NDDB & BIS), colorimetric adulteration screening, Flieg fermentation scoring, and feed bag QR authenticity.",
    ingredient: "What is this feed?",
    ingredient_name: "Select or type feed name",
    form_ing: "Raw Fodder",
    form_sil: "Silage",
    form_cmp: "Compounded",
    moisture: "Moisture %",
    ph: "Silage pH",
    urea: "4-DMAB Yellow %",
    mould: "Visible Mould Detected",
    photo: "Upload Feed Photo for Mould Verification",
    test: "Assess Feed Quality Now",
    testing: "Assessing Quality...",
    cp: "Crude Protein % DM",
    asfed: "CP as-fed %",
    method: "Method",
    flieg: "Flieg Score",
    moisture_dm: "Dry Matter %",
    urea_est: "Urea g/kg (screen)",
    af: "AFB1 Risk (historical)",
    why: "Primary Reasons",
    none: "—",
    sand: "Sand & Silica Adulteration (Jar Test / Lab AIA)",
    ration: "How to use in today's ration",
    also: "Also noted",
    sensor: "Sensor check",
    hear: "Hear Spoken Advice",
    tab_test: "Assess Feed",
    tab_qr: "Verify Bag",
    tab_result: "Verdict & Advice",
    tab_models: "Sensor Kit & Models",
    qr_heading: "Feed Bag QR Authenticity Verification",
    qr_tab_title: "Feed Bag Authenticity Scanner",
    qr_tab_desc: "Scan or upload the QR code printed on cattle feed bags to verify expiry dates, manufacturer license, and declared nutrients against Indian tables.",
    result_empty: "Configure feed readings on the Assess Feed tab and tap Assess Feed Quality. Detailed safety verdicts and ration advice will appear right here.",
    models_lead: "Weights live on this device pack, not inside a web page. Replace a file in models/ and tap Update.",
    models_update: "Update & Reload Pack",
    models_updating: "Updating...",
    models_done: "Pack reloaded. Next test uses the new files.",
    kit_none: "No kit reading on the server yet.",
    kit_ok: "Kit {id} · moisture {m}%{ph}{chip}",
    kit_chip: " · 18 colour bands (not protein)",
  },
  hi: {
    hero_title: "पशु आहार एवं साइलेज गुणवत्ता की त्वरित डिजिटल जाँच",
    hero_desc: "भारतीय डेरी तालिकाओं (NDDB व BIS), यूरिया मिलावट जाँच, Flieg साइलेज स्कोरिंग और बोरी QR प्रामाणिकता पर आधारित डिजिटल प्रणाली।",
    ingredient: "यह चारा क्या है?",
    ingredient_name: "चारे का नाम चुनें या लिखें",
    form_ing: "कच्चा चारा",
    form_sil: "साइलेज",
    form_cmp: "मिश्रित दाना",
    moisture: "नमी %",
    ph: "साइलेज pH",
    urea: "4-DMAB पीला %",
    mould: "दिखने वाली फफूंद",
    photo: "फफूंद जाँच के लिए फोटो अपलोड करें",
    test: "गुणवत्ता जाँचें",
    testing: "जाँच हो रही है...",
    cp: "क्रूड प्रोटीन % DM",
    asfed: "CP जैसा खिलाया %",
    method: "विधि",
    flieg: "Flieg अंक",
    moisture_dm: "शुष्क पदार्थ %",
    urea_est: "यूरिया ग्रा/किग्रा",
    af: "AFB1 जोखिम",
    why: "मुख्य कारण",
    none: "—",
    sand: "रेत व सिलिका मिलावट जाँच",
    ration: "आज के राशन में कैसे उपयोग करें",
    also: "अन्य बातें",
    sensor: "सेंसर चेतावनी",
    hear: "सलाह सुनें",
    tab_test: "आहार जाँच",
    tab_qr: "बोरी जाँच",
    tab_result: "फैसला व सलाह",
    tab_models: "किट व मॉडल",
    qr_heading: "बोरी QR प्रामाणिकता जाँच",
    qr_tab_title: "पशु आहार बोरी प्रामाणिकता स्कैनर",
    qr_tab_desc: "बोरी पर छपे QR कोड को स्कैन करके समाप्ति तिथि, निर्माता लाइसेंस और पोषक तत्वों की जाँच करें।",
    result_empty: "आहार जाँच टैब में विवरण भरें और गुणवत्ता जाँचें दबाएँ। पूरा फैसला और सलाह यहाँ दिखाई देगी।",
    models_lead: "मॉडल वेट डिस्क पर हैं। फ़ाइल बदलकर अपडेट दबाएँ।",
    models_update: "अपडेट और रीलोड",
    models_updating: "अपडेट हो रहा है...",
    models_done: "पैक रीलोड हुआ।",
    kit_none: "सर्वर पर किट रीडिंग नहीं है।",
    kit_ok: "किट {id} · नमी {m}%{ph}{chip}",
    kit_chip: " · 18 रंग बैंड",
  },
};

let lang = "en";
let lastSpoken = { en: "", hi: "" };
let kitSpectrum = null;
let activeScanner = null;
let activeScannerId = null;

function t(key) {
  return (I18N[lang] && I18N[lang][key]) || (I18N.en && I18N.en[key]) || key;
}

function applyLang() {
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.dataset.i18n;
    if (key) el.textContent = t(key);
  });
  document.getElementById("lang-en")?.classList.toggle("active", lang === "en");
  document.getElementById("lang-hi")?.classList.toggle("active", lang === "hi");
  const spoken = document.getElementById("spoken-text");
  if (spoken && (lastSpoken.en || lastSpoken.hi)) {
    spoken.textContent = lastSpoken[lang] || lastSpoken.en;
  }
}

function showScreen(name) {
  if (name !== "qr" && activeScannerId === "tab-qr-reader") {
    stopAnyQrScanner();
  }
  document.querySelectorAll(".screen").forEach((el) => {
    el.classList.toggle("hidden", el.id !== `screen-${name}`);
  });
  document.querySelectorAll(".portal-tab-btn").forEach((el) => {
    el.classList.toggle("active", el.dataset.screen === name);
  });
  document.querySelectorAll(".mobile-nav-btn").forEach((el) => {
    el.classList.toggle("active", el.dataset.screen === name);
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
  if (span.min != null && span.max != null) return `${span.mean} (${span.min}–${span.max})`;
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

  document.getElementById("result-empty")?.classList.add("hidden");
  const box = document.getElementById("result");
  if (!box) return;
  box.classList.remove("hidden");

  box.innerHTML = `
    <div class="stamp ${action}">
      <h2>${label || action}</h2>
      <p>${summary || ""}</p>
    </div>

    <div class="audio-bar">
      <div class="spoken-preview" id="spoken-text">${spoken}</div>
      <button type="button" id="hear" class="audio-btn">🔊 ${t("hear")}</button>
    </div>

    <div class="metric-grid">
      <div class="metric"><span>${t("cp")}</span><b>${spanText(cp)}</b></div>
      <div class="metric"><span>${t("asfed")}</span><b>${spanText(asfed)}</b></div>
      <div class="metric"><span>${t("method")}</span><b>${nut.method || t("none")}</b></div>
      <div class="metric"><span>${t("moisture_dm")}</span><b>${moist.dry_matter_pct ?? t("none")}</b></div>
      <div class="metric"><span>${t("flieg")}</span><b>${silage.flieg_score ?? t("none")}</b></div>
      <div class="metric"><span>${t("urea_est")}</span><b>${urea.urea_g_per_kg ?? t("none")}</b></div>
    </div>

    <div class="advice-block">
      <h4>${t("why")}</h4>
      <ul>${(reasons || []).map((r) => `<li>${r}</li>`).join("")}</ul>
    </div>

    ${other.length ? `
      <div class="advice-block">
        <h4>${t("also")}</h4>
        <ul>${other.map((r) => `<li>${r}</li>`).join("")}</ul>
      </div>
    ` : ""}

    ${tips.length ? `
      <div class="advice-block mineral">
        <h4>${t("ration")}${role ? ` — ${role}` : ""}</h4>
        <ul>${tips.map((r) => `<li>${r}</li>`).join("")}</ul>
      </div>
    ` : ""}

    ${warns.length ? `
      <div class="advice-block" style="border-left:4px solid #c22929;">
        <h4 style="color:#c22929;">${t("sensor")}</h4>
        <ul style="color:#c22929;">${warns.map((r) => `<li>${r}</li>`).join("")}</ul>
      </div>
    ` : ""}

    ${renderQrResult(data)}

    <div style="margin-top:24px;display:flex;gap:12px;">
      <button type="button" class="btn-primary" id="btn-test-another">← Test Another Feed</button>
    </div>

    <p style="font-size:0.78rem;color:var(--muted);margin-top:16px;">${data.disclaimer || ""}</p>
  `;

  document.getElementById("hear")?.addEventListener("click", speakAdvice);
  document.getElementById("btn-test-another")?.addEventListener("click", () => {
    showScreen("test");
    document.getElementById("test-portal")?.scrollIntoView({ behavior: "smooth" });
  });

  // Switch to Verdict & Advice tab and scroll into view smoothly
  showScreen("result");
  document.getElementById("test-portal")?.scrollIntoView({ behavior: "smooth" });
}

function renderQrResult(data) {
  const qr = (data.modules || {}).qr;
  if (!qr || !qr.present || !qr.decoded) return "";
  const bag = qr.bag_info || {};
  const statusClass = qr.verified ? "verified" : "danger";
  const badgeClass = qr.verified ? "green" : "red";
  const statusLabel = qr.verified
    ? (lang === "hi" ? "✓ बोरी सत्यापित (मानक अनुसार)" : "✓ BAG VERIFIED (STANDARDS MATCH)")
    : (qr.expired
      ? (lang === "hi" ? "✗ बोरी समाप्त (एक्सपायर्ड)" : "✗ BAG EXPIRED")
      : (lang === "hi" ? "⚠ विवरण में अंतर" : "⚠ DECLARATION MISMATCH"));
  const warns = (qr.warnings || []).map((w) => `<li>${w}</li>`).join("");

  return `
    <div class="qr-bag-card ${statusClass}">
      <span class="qr-badge ${badgeClass}">${statusLabel}</span>
      <h4 style="font-size:1.05rem;color:var(--forest-dark);margin:4px 0;">${bag.manufacturer || "—"}</h4>
      <dl class="qr-kv">
        <dt>Batch No:</dt><dd>${bag.batch_no || "—"}</dd>
        <dt>Expiry Date:</dt><dd>${bag.expiry_date || "—"}</dd>
        <dt>Declared CP:</dt><dd>${bag.declared_cp_pct_dm ?? "—"}% DM</dd>
        <dt>Declared Moisture:</dt><dd>${bag.declared_moisture_pct ?? "—"}%</dd>
      </dl>
      ${warns ? `<ul style="color:#c22929;font-size:0.84rem;margin-top:8px;">${warns}</ul>` : ""}
    </div>
  `;
}

// ----------------------------------------------------
// QR Code Camera & File Scanner Module
// ----------------------------------------------------

const PRESET_QR = {
  valid: "eyJtYW51ZmFjdHVyZXIiOiAiQW11bCBGZWVkIENvIiwgImJhdGNoX25vIjogIkIyMDI2LTA5IiwgInBhY2tfZGF0ZSI6ICIyMDI2LTA4LTAxIiwgImV4cGlyeV9kYXRlIjogIjIwMjctMDgtMDEiLCAiZGVjbGFyZWRfY3BfcGN0X2RtIjogMzYuMCwgImRlY2xhcmVkX21vaXN0dXJlX3BjdCI6IDEwLjAsICJiaXNfbGljZW5zZSI6ICJDTS9MLTEyMzQ1NjcifQ==",
  expired: "eyJtYW51ZmFjdHVyZXIiOiAiS2FpcmEgVW5pb24gRmVlZCIsICJiYXRjaF9ubyI6ICJFWFAtOTkiLCAicGFja19kYXRlIjogIjIwMTktMDEtMTAiLCAiZXhwaXJ5X2RhdGUiOiAiMjAyMC0wMS0xMCIsICJkZWNsYXJlZF9jcF9wY3RfZG0iOiAzNS4wLCAiZGVjbGFyZWRfbW9pc3R1cmVfcGN0IjogMTEuMH0=",
  mismatch: "eyJtYW51ZmFjdHVyZXIiOiAiQ2hlYXBGZWVkcyBMdGQiLCAiYmF0Y2hfbm8iOiAiTS0wNDIiLCAicGFja19kYXRlIjogIjIwMjYtMDYtMDEiLCAiZXhwaXJ5X2RhdGUiOiAiMjAyNy0wNi0wMSIsICJkZWNsYXJlZF9jcF9wY3RfZG0iOiAxMi4wLCAiZGVjbGFyZWRfbW9pc3R1cmVfcGN0IjogMTAuMH0=",
};

function parseQrPayload(payload) {
  try {
    let b64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    while (b64.length % 4) b64 += "=";
    const jsonStr = decodeURIComponent(escape(atob(b64)));
    return JSON.parse(jsonStr);
  } catch (e) {
    try {
      return JSON.parse(atob(payload));
    } catch (_) {
      return null;
    }
  }
}

async function stopAnyQrScanner() {
  if (activeScanner) {
    try {
      await activeScanner.stop();
    } catch (_) {}
    try {
      activeScanner.clear();
    } catch (_) {}
    activeScanner = null;
    activeScannerId = null;
  }
  document.getElementById("test-qr-video")?.classList.add("hidden");
  document.getElementById("tab-qr-scanner-box")?.classList.add("hidden");
  document.getElementById("btn-stop-tab-scanner")?.classList.add("hidden");
  document.getElementById("btn-start-tab-scanner")?.classList.remove("hidden");
}

async function startCameraScan(containerId, onScanSuccess) {
  await stopAnyQrScanner();
  if (typeof Html5Qrcode === "undefined") {
    alert("Camera scanner library is loading, please try again in a moment.");
    return;
  }
  const boxEl = containerId === "test-qr-reader"
    ? document.getElementById("test-qr-video")
    : document.getElementById("tab-qr-scanner-box");
  boxEl?.classList.remove("hidden");

  if (containerId === "tab-qr-reader") {
    document.getElementById("btn-start-tab-scanner")?.classList.add("hidden");
    document.getElementById("btn-stop-tab-scanner")?.classList.remove("hidden");
  }

  const scanner = new Html5Qrcode(containerId);
  activeScanner = scanner;
  activeScannerId = containerId;

  try {
    await scanner.start(
      { facingMode: "environment" },
      { fps: 10, qrbox: { width: 250, height: 250 } },
      async (decodedText) => {
        await stopAnyQrScanner();
        onScanSuccess(decodedText);
      },
      () => {}
    );
  } catch (err) {
    await stopAnyQrScanner();
    alert("Camera error: " + (err.message || err));
  }
}

async function scanImageFile(file, onScanSuccess) {
  if (!file) return;
  if (typeof Html5Qrcode === "undefined") {
    alert("Scanner library loading, please wait.");
    return;
  }
  const helper = new Html5Qrcode("tab-qr-reader");
  try {
    const decodedText = await helper.scanFile(file, true);
    onScanSuccess(decodedText);
  } catch (err) {
    alert("Could not detect a QR code in this image: " + (err.message || err));
  } finally {
    try { helper.clear(); } catch (_) {}
  }
}

function renderDecodedBagCard(payload, containerEl, isTab = false) {
  const bag = parseQrPayload(payload);
  if (!bag) {
    containerEl.classList.remove("hidden");
    containerEl.className = "qr-bag-card danger";
    containerEl.innerHTML = `<span class="qr-badge red">INVALID QR</span><p style="margin:4px 0;">Scanned payload could not be decoded as valid feed bag JSON.</p>`;
    return;
  }

  const isExpired = bag.expiry_date && new Date(bag.expiry_date) < new Date();
  const cardClass = isExpired ? "danger" : "verified";
  const badgeClass = isExpired ? "red" : "green";
  const badgeText = isExpired
    ? (lang === "hi" ? "✗ बोरी समाप्त (एक्सपायर्ड)" : "✗ BAG EXPIRED")
    : (lang === "hi" ? "✓ बोरी विवरण प्राप्त" : "✓ VALID BAG SPEC");

  containerEl.classList.remove("hidden");
  containerEl.className = `qr-bag-card ${cardClass}`;
  containerEl.innerHTML = `
    <span class="qr-badge ${badgeClass}">${badgeText}</span>
    <h4 style="font-size:1.1rem;color:var(--forest-dark);margin:2px 0 6px;">${bag.manufacturer || "Unknown Manufacturer"}</h4>
    <dl class="qr-kv">
      <dt>Batch No:</dt><dd>${bag.batch_no || "—"}</dd>
      <dt>Packed:</dt><dd>${bag.pack_date || "—"}</dd>
      <dt>Expiry:</dt><dd>${bag.expiry_date || "—"} ${isExpired ? "<strong>(EXPIRED)</strong>" : ""}</dd>
      <dt>Declared CP:</dt><dd>${bag.declared_cp_pct_dm ?? "—"}% DM</dd>
      <dt>Declared Moisture:</dt><dd>${bag.declared_moisture_pct ?? "—"}%</dd>
      ${bag.bis_license ? `<dt>BIS License:</dt><dd>${bag.bis_license}</dd>` : ""}
    </dl>
    ${isTab ? `
      <div style="margin-top:14px;">
        <button type="button" class="btn-primary btn-sm" id="btn-use-qr-in-test">
          ${lang === "hi" ? "आहार जाँच में इस्तेमाल करें" : "Use in Feed Test"}
        </button>
      </div>
    ` : ""}
  `;

  if (isTab) {
    document.getElementById("btn-use-qr-in-test")?.addEventListener("click", () => {
      applyPayloadToForm(payload, bag);
      showScreen("test");
      document.getElementById("test-portal")?.scrollIntoView({ behavior: "smooth" });
    });
  }
}

function applyPayloadToForm(payload, bag = null) {
  if (!bag) bag = parseQrPayload(payload);
  const hiddenInput = document.getElementById("qr_payload");
  if (hiddenInput) hiddenInput.value = payload;
  const infoEl = document.getElementById("test-qr-info");
  if (infoEl) renderDecodedBagCard(payload, infoEl, false);
  document.getElementById("btn-clear-test-qr")?.classList.remove("hidden");

  const ingInput = document.getElementById("ingredient");
  if (ingInput && (!ingInput.value || ingInput.value === "wheat straw")) {
    ingInput.value = bag?.feed_type || "mustard cake";
  }
  const moistInput = document.getElementById("moisture");
  if (moistInput && bag?.declared_moisture_pct) {
    moistInput.value = bag.declared_moisture_pct;
  }
}

function clearFormQr() {
  const hiddenInput = document.getElementById("qr_payload");
  if (hiddenInput) hiddenInput.value = "";
  const infoEl = document.getElementById("test-qr-info");
  if (infoEl) {
    infoEl.innerHTML = "";
    infoEl.classList.add("hidden");
  }
  document.getElementById("btn-clear-test-qr")?.classList.add("hidden");
  stopAnyQrScanner();
}

// ----------------------------------------------------
// Setup Event Listeners
// ----------------------------------------------------

// Language Toggles
document.getElementById("lang-en")?.addEventListener("click", () => { lang = "en"; applyLang(); });
document.getElementById("lang-hi")?.addEventListener("click", () => { lang = "hi"; applyLang(); });

// Category Chips Selection
document.querySelectorAll(".cat-chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    document.querySelectorAll(".cat-chip").forEach((c) => c.classList.remove("selected"));
    chip.classList.add("selected");
    const radio = chip.querySelector("input[type=radio]");
    if (radio) {
      radio.checked = true;
      const phInput = document.getElementById("ph");
      if (radio.value === "silage") {
        if (phInput && !phInput.value) phInput.value = "3.9";
        const ingInput = document.getElementById("ingredient");
        if (ingInput && ingInput.value === "wheat straw") ingInput.value = "maize silage";
      }
    }
  });
});

// Portal Tabs
document.querySelectorAll(".portal-tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const screen = btn.dataset.screen;
    if (screen) showScreen(screen);
  });
});

// Mobile Bottom Navigation Tabs
document.querySelectorAll(".mobile-nav-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const screen = btn.dataset.screen;
    if (screen) {
      showScreen(screen);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  });
});

// Hero Buttons
document.getElementById("btn-hero-start")?.addEventListener("click", (e) => {
  e.preventDefault();
  showScreen("test");
  document.getElementById("test-portal")?.scrollIntoView({ behavior: "smooth" });
});
document.getElementById("btn-hero-qr")?.addEventListener("click", () => {
  showScreen("qr");
  document.getElementById("test-portal")?.scrollIntoView({ behavior: "smooth" });
});

// Test Form QR Listeners
document.getElementById("btn-scan-test-qr")?.addEventListener("click", () => {
  startCameraScan("test-qr-reader", (payload) => {
    applyPayloadToForm(payload);
  });
});
document.getElementById("btn-stop-test-qr")?.addEventListener("click", () => {
  stopAnyQrScanner();
});
document.getElementById("input-test-qr-file")?.addEventListener("change", (ev) => {
  const file = ev.target.files[0];
  if (file) {
    scanImageFile(file, (payload) => {
      applyPayloadToForm(payload);
    });
  }
});
document.getElementById("btn-sample-test-qr")?.addEventListener("click", () => {
  applyPayloadToForm(PRESET_QR.valid);
});
document.getElementById("btn-clear-test-qr")?.addEventListener("click", () => {
  clearFormQr();
});

// Dedicated QR Tab Listeners
document.getElementById("btn-start-tab-scanner")?.addEventListener("click", () => {
  startCameraScan("tab-qr-reader", (payload) => {
    const resEl = document.getElementById("tab-qr-result");
    if (resEl) renderDecodedBagCard(payload, resEl, true);
  });
});
document.getElementById("btn-stop-tab-scanner")?.addEventListener("click", () => {
  stopAnyQrScanner();
});
document.getElementById("input-tab-qr-file")?.addEventListener("change", (ev) => {
  const file = ev.target.files[0];
  if (file) {
    scanImageFile(file, (payload) => {
      const resEl = document.getElementById("tab-qr-result");
      if (resEl) renderDecodedBagCard(payload, resEl, true);
    });
  }
});
document.getElementById("btn-preset-valid")?.addEventListener("click", () => {
  const resEl = document.getElementById("tab-qr-result");
  if (resEl) renderDecodedBagCard(PRESET_QR.valid, resEl, true);
});
document.getElementById("btn-preset-expired")?.addEventListener("click", () => {
  const resEl = document.getElementById("tab-qr-result");
  if (resEl) renderDecodedBagCard(PRESET_QR.expired, resEl, true);
});
document.getElementById("btn-preset-mismatch")?.addEventListener("click", () => {
  const resEl = document.getElementById("tab-qr-result");
  if (resEl) renderDecodedBagCard(PRESET_QR.mismatch, resEl, true);
});

// Photo Preview
document.getElementById("photo")?.addEventListener("change", (ev) => {
  const file = ev.target.files[0];
  const container = document.getElementById("photo-preview-container");
  const img = document.getElementById("photo-preview");
  if (!file || !img || !container) return;
  img.src = URL.createObjectURL(file);
  container.classList.remove("hidden");
});

// Form Submission Handler
document.getElementById("kit")?.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const btn = document.getElementById("btn-test-submit");
  if (btn) {
    btn.disabled = true;
    btn.textContent = t("testing");
  }

  const fd = new FormData();
  fd.append("ingredient", document.getElementById("ingredient").value);
  fd.append("form", document.querySelector("input[name=form]:checked")?.value || "ingredient");

  const moisture = num(document.getElementById("moisture").value);
  const ph = num(document.getElementById("ph").value);
  const urea = num(document.getElementById("urea").value);
  if (moisture !== "") fd.append("moisture_pct", moisture);
  if (ph !== "") fd.append("ph", ph);
  if (urea !== "") fd.append("urea_yellow_area_pct", urea);

  for (const [id, field] of [["grit", "grit_settled_ml"], ["sample_g", "sample_g"], ["aia", "aia_pct"]]) {
    const el = document.getElementById(id);
    if (el) {
      const v = num(el.value);
      if (v !== "") fd.append(field, v);
    }
  }

  const mouldEl = document.getElementById("mould");
  if (mouldEl) fd.append("visible_mould", mouldEl.checked);
  if (kitSpectrum) fd.append("nir_json", JSON.stringify(kitSpectrum));

  const qrVal = document.getElementById("qr_payload")?.value?.trim();
  if (qrVal) fd.append("qr_payload", qrVal);

  const photo = document.getElementById("photo")?.files?.[0];
  if (photo) fd.append("photo", photo);

  try {
    const res = await fetch("/api/assess", { method: "POST", body: fd });
    if (!res.ok) throw new Error(await res.text());
    render(await res.json());
  } catch (err) {
    document.getElementById("result-empty")?.classList.add("hidden");
    const box = document.getElementById("result");
    if (box) {
      box.classList.remove("hidden");
      box.innerHTML = `<div class="stamp reject"><h2>ERROR</h2><p>${err.message}</p></div>`;
    }
    showScreen("result");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = t("test");
    }
  }
});

// Sensor Kit Integration
async function pullKit() {
  try {
    const res = await fetch("/api/kit");
    const data = await res.json();
    const reading = data.reading;
    const status = document.getElementById("kit-status");
    if (!reading) {
      if (status) status.textContent = t("kit_none");
      return;
    }
    if (reading.moisture_pct != null) document.getElementById("moisture").value = reading.moisture_pct;
    if (reading.ph != null) document.getElementById("ph").value = reading.ph;
    kitSpectrum = Array.isArray(reading.as7265x) ? reading.as7265x : null;
    const phBit = reading.ph != null ? ` · pH ${reading.ph}` : "";
    const chipBit = kitSpectrum ? t("kit_chip") : "";
    if (status) {
      status.textContent = t("kit_ok")
        .replace("{id}", reading.device_id || "kit")
        .replace("{m}", reading.moisture_pct ?? "—")
        .replace("{ph}", phBit)
        .replace("{chip}", chipBit);
    }
  } catch (_) {}
}
document.getElementById("kit-pull")?.addEventListener("click", () => pullKit());

// Models Pack
async function loadIngredients() {
  try {
    const res = await fetch("/api/ingredients");
    const data = await res.json();
    const list = document.getElementById("ingredient-list");
    if (list) {
      list.innerHTML = data.items.map((it) => `<option value="${it.canonical}"></option>`).join("");
    }
  } catch (_) {}
}

async function loadModels() {
  try {
    const res = await fetch("/api/models");
    const pack = await res.json();
    const metaEl = document.getElementById("models-meta");
    if (metaEl) {
      metaEl.textContent = `v${pack.version} · ${pack.files.length} files · ${kb(pack.total_bytes)} · ${pack.updated || ""}`;
    }
    const listEl = document.getElementById("models-list");
    if (listEl) {
      listEl.innerHTML = (pack.files || []).map((f) => `
        <li style="padding:8px 0;border-bottom:1px solid #e0e0e0;">
          <strong>${f.file}</strong>
          <div style="font-size:0.8rem;color:#555;">${f.role} · ${kb(f.bytes)} · ${f.sha256_16}</div>
        </li>
      `).join("");
    }
  } catch (_) {}
}

// Initial Invocations
applyLang();
loadIngredients().catch(() => {});
pullKit().catch(() => {});
