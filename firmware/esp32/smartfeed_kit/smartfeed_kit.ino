/*
  SmartFeed India — ESP32 measurement probe.

  This board only reads sensors. Tables, Flieg, urea, sand and the verdict
  live in the Flutter app (mobile/assets/offline_kit.json). AS7265x 18 bands
  are logged and never scored as crude protein.
*/

#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <Wire.h>
#include "config.h"
#include "web_ui.h"

#if __has_include(<SparkFun_AS7265X.h>)
#include <SparkFun_AS7265X.h>
#define HAS_AS7265X 1
SparkFun_AS7265X as7265x;
#endif

static WebServer server(80);
static DNSServer dns;
static bool as7265x_ok = false;

static float clampf(float v, float lo, float hi) {
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}

static float read_moisture_pct() {
  analogSetPinAttenuation(PIN_MOISTURE, ADC_11db);
  uint32_t acc = 0;
  for (int i = 0; i < 8; i++) {
    acc += analogRead(PIN_MOISTURE);
    delay(4);
  }
  int raw = (int)(acc / 8);
  float pct = 100.0f * (float)(MOISTURE_DRY - raw) / (float)(MOISTURE_DRY - MOISTURE_WET);
  return clampf(pct, 0.0f, 100.0f);
}

static bool read_ph(float *out) {
  if (PIN_PH < 0) return false;
  analogSetPinAttenuation(PIN_PH, ADC_11db);
  uint32_t acc = 0;
  for (int i = 0; i < 8; i++) {
    acc += analogRead(PIN_PH);
    delay(4);
  }
  float volt = (acc / 8.0f) * PH_VREF / PH_ADC_MAX;
  *out = clampf(7.0f + (PH_MID_VOLT - volt) / PH_SLOPE, 0.0f, 14.0f);
  return true;
}

#ifdef HAS_AS7265X
static bool fill_as7265x(float *bands) {
  if (!as7265x_ok) return false;
  as7265x.takeMeasurementsWithBulb();
  bands[0] = as7265x.getCalibratedA();
  bands[1] = as7265x.getCalibratedB();
  bands[2] = as7265x.getCalibratedC();
  bands[3] = as7265x.getCalibratedD();
  bands[4] = as7265x.getCalibratedE();
  bands[5] = as7265x.getCalibratedF();
  bands[6] = as7265x.getCalibratedG();
  bands[7] = as7265x.getCalibratedH();
  bands[8] = as7265x.getCalibratedR();
  bands[9] = as7265x.getCalibratedI();
  bands[10] = as7265x.getCalibratedS();
  bands[11] = as7265x.getCalibratedJ();
  bands[12] = as7265x.getCalibratedT();
  bands[13] = as7265x.getCalibratedU();
  bands[14] = as7265x.getCalibratedV();
  bands[15] = as7265x.getCalibratedW();
  bands[16] = as7265x.getCalibratedK();
  bands[17] = as7265x.getCalibratedL();
  return true;
}
#endif

static void handle_root() {
  server.send_P(200, "text/html; charset=utf-8", INDEX_HTML);
}

static void handle_sensors() {
  float m = read_moisture_pct();
  float ph = 0;
  bool have_ph = read_ph(&ph);
  String json = "{\"device_id\":\"";
  json += DEVICE_ID;
  json += "\",\"role\":\"measurement_only\",\"models_on_board\":false";
  json += ",\"moisture_pct\":";
  json += String(m, 2);
  if (have_ph) {
    json += ",\"ph\":";
    json += String(ph, 2);
  } else {
    json += ",\"ph\":null";
  }
  json += ",\"as7265x_ok\":";
  json += as7265x_ok ? "true" : "false";
  json += ",\"as7265x_used_for_cp\":false";
#ifdef HAS_AS7265X
  float bands[18];
  if (fill_as7265x(bands)) {
    json += ",\"as7265x\":[";
    for (int i = 0; i < 18; i++) {
      if (i) json += ",";
      json += String(bands[i], 4);
    }
    json += "]";
  } else {
    json += ",\"as7265x\":null";
  }
#else
  json += ",\"as7265x\":null";
#endif
  json += "}";
  server.send(200, "application/json; charset=utf-8", json);
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  Wire.begin(I2C_SDA, I2C_SCL);

#ifdef HAS_AS7265X
  as7265x_ok = as7265x.begin();
  if (as7265x_ok) {
    as7265x.setMeasurementMode(AS7265X_MEASUREMENT_MODE_6CHAN_CONTINUOUS);
    Serial.println("AS7265x present — logged only, not used for CP.");
  }
#endif

#if OFFLINE_AP
  WiFi.mode(WIFI_AP);
  if (strlen(AP_PASS) >= 8) WiFi.softAP(AP_SSID, AP_PASS);
  else WiFi.softAP(AP_SSID);
  delay(200);
  IPAddress ip = WiFi.softAPIP();
  dns.start(53, "*", ip);
  Serial.print("Probe AP ");
  Serial.print(AP_SSID);
  Serial.print("  sensors http://");
  Serial.println(ip);
#else
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
#endif

  server.on("/", handle_root);
  server.on("/api/sensors", handle_sensors);
  server.onNotFound(handle_root);
  server.begin();
}

void loop() {
#if OFFLINE_AP
  dns.processNextRequest();
#endif
  server.handleClient();
}
