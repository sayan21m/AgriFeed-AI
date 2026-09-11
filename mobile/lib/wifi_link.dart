import 'dart:io';

import 'package:permission_handler/permission_handler.dart';
import 'package:wifi_iot/wifi_iot.dart';

const kitWifiSsid = 'SmartFeed';

enum WifiJoin { ok, failed, needWifi, needPermission, skipped }

String? cleanSsid(String? raw) {
  if (raw == null) return null;
  return raw.replaceAll('"', '').trim();
}

/// Join the ESP32 SoftAP. Farmers never open phone Wi-Fi settings.
Future<WifiJoin> joinSmartFeedAp() async {
  if (!Platform.isAndroid && !Platform.isIOS) return WifiJoin.skipped;

  final allowed = await _askWifiPermission();

  try {
    if (Platform.isAndroid) {
      final on = await WiFiForIoTPlugin.isEnabled();
      if (on != true) {
        await WiFiForIoTPlugin.setEnabled(true, shouldOpenSettings: false);
        await Future<void>.delayed(const Duration(milliseconds: 600));
        if (await WiFiForIoTPlugin.isEnabled() != true) {
          return WifiJoin.needWifi;
        }
      }
    }

    final current = cleanSsid(await WiFiForIoTPlugin.getSSID());
    if (current != kitWifiSsid) {
      final ok = await WiFiForIoTPlugin.connect(
        kitWifiSsid,
        password: '',
        security: NetworkSecurity.NONE,
        joinOnce: true,
        withInternet: false,
        timeoutInSeconds: 25,
      );
      if (ok != true) return allowed ? WifiJoin.failed : WifiJoin.needPermission;
    }

    if (Platform.isAndroid) {
      await WiFiForIoTPlugin.forceWifiUsage(true);
    }
    await Future<void>.delayed(const Duration(milliseconds: 700));
    return WifiJoin.ok;
  } catch (_) {
    return WifiJoin.failed;
  }
}

Future<bool> _askWifiPermission() async {
  if (Platform.isIOS) {
    final status = await Permission.locationWhenInUse.request();
    return status.isGranted || status.isLimited;
  }

  var ok = false;
  final location = await Permission.locationWhenInUse.request();
  if (location.isGranted || location.isLimited) ok = true;
  try {
    final nearby = await Permission.nearbyWifiDevices.request();
    if (nearby.isGranted) ok = true;
  } catch (_) {}
  return ok;
}
