#pragma once

// Measurement probe: phone joins Wi-Fi "SmartFeed" and taps Use kit.
// Scoring is on the phone. This board only serves GET /api/sensors.
#define OFFLINE_AP        1
#define AP_SSID           "SmartFeed"
#define AP_PASS           ""   // empty = open network

// Optional: also join a home Wi-Fi (leave OFFLINE_AP 1 for the field kit).
#define WIFI_SSID         "YOUR_WIFI"
#define WIFI_PASSWORD     "YOUR_PASSWORD"

#define DEVICE_ID         "smartfeed-kit-01"

#define PIN_MOISTURE      34
#define MOISTURE_DRY      2800
#define MOISTURE_WET      1200

#define PIN_PH            35
#define PH_VREF           3.3f
#define PH_ADC_MAX        4095.0f
#define PH_MID_VOLT       1.65f
#define PH_SLOPE          0.18f

#define I2C_SDA           21
#define I2C_SCL           22
#define AS7265X_ADDR      0x49
