class L10n {
  L10n(this.hi);
  final bool hi;

  String get title => 'AgriFeed-AI';
  String get kicker => hi ? 'SIH26111 · पशुपालन विभाग' : 'SIH26111 · DAHD';
  String get tagline => hi ? 'गाँव का पशु आहार किट' : 'Village cattle feed kit';
  String get heroLine =>
      hi ? 'बोरी का नाम बताएँ। गड्ढे की जाँच करें।' : 'Name the bag. Test the pit.';
  String get ingredient => hi ? 'यह चारा क्या है?' : 'What is this feed?';
  String get camera => hi ? 'कैमरा' : 'Camera';
  String get gallery => hi ? 'गैलरी' : 'Gallery';
  String get sectionFeed => hi ? 'चारा' : 'Feed';
  String get sectionSensors => hi ? 'सेंसर' : 'Sensors';
  String get emptyVerdictTitle => hi ? 'अभी कोई फैसला नहीं' : 'No verdict yet';
  String get form => hi ? 'प्रकार' : 'Form';
  String get formIng => hi ? 'कच्चा चारा' : 'Ingredient';
  String get formSil => hi ? 'साइलेज' : 'Silage';
  String get formCmp => hi ? 'मिश्रित दाना' : 'Compounded';
  String get moisture => hi ? 'नमी %' : 'Moisture %';
  String get ph => hi ? 'साइलेज pH' : 'Silage pH';
  String get urea => hi ? '4-DMAB पीला %' : '4-DMAB yellow %';
  String get mould => hi ? 'दिखने वाली फफूंद' : 'Visible mould';
  String get photo => hi ? 'फोन फोटो (फफूंद)' : 'Phone photo (mould)';
  String get test => hi ? 'अभी जाँचें' : 'Test now';
  String get testing => hi ? 'जाँच हो रही है…' : 'Testing…';
  String get kit => hi ? 'सेंसर बोर्ड' : 'Sensor board';
  String get kitPull => hi ? 'जोड़ें' : 'Connect';
  String get kitLooking => hi ? 'जोड़ रहे हैं…' : 'Connecting…';
  String get kitConnected => hi ? 'जुड़ा हुआ' : 'Connected';
  String get kitOffline => hi ? 'नहीं जुड़ा' : 'Not connected';
  String get kitIdle =>
      hi ? 'बोर्ड चालू करें, फिर जोड़ें दबाएँ।' : 'Switch the board on, then tap Connect.';
  String get kitNone =>
      hi ? 'बोर्ड नहीं मिला। उसे चालू करें, फिर जोड़ें दबाएँ।' : 'Board not found. Switch it on, then tap Connect.';
  String get kitNeedWifi =>
      hi ? 'फ़ोन की वाई-फ़ाई चालू करें, फिर जोड़ें दबाएँ।' : 'Turn the phone Wi-Fi on, then tap Connect.';
  String get kitNeedPerm =>
      hi ? 'वाई-फ़ाई की अनुमति दें, फिर जोड़ें दबाएँ।' : 'Allow Wi-Fi permission, then tap Connect.';
  String get kitHow => hi ? 'बोर्ड कैसे जोड़ें' : 'How to use the board';
  String get kitStep1 => hi ? 'बोर्ड चालू करें (पावर बैंक काफी है)।' : 'Switch the board on (a power bank is enough).';
  String get kitStep2 =>
      hi ? 'जोड़ें दबाएँ। फ़ोन पूछे तो अनुमति दें।' : 'Tap Connect. If the phone asks, tap Allow.';
  String get kitStep3 =>
      hi ? 'नमी और pH अपने आप भर जाएँगे।' : 'Moisture and pH fill in by themselves.';
  String kitReadings(String moisture, String ph, bool chip) {
    final chipBit = chip
        ? (hi ? ' · रंग चिप चालू' : ' · colour chip on')
        : '';
    final phBit = ph == none ? '' : ' · pH $ph';
    return hi ? 'नमी $moisture%$phBit$chipBit' : 'Moisture $moisture%$phBit$chipBit';
  }
  String get sand => hi ? 'रेत / सिलिका' : 'Sand / silica';
  String get grit => hi ? 'बैठी हुई रेत (मिली)' : 'Settled grit (ml)';
  String get sampleG => hi ? 'नमूने का वज़न (ग्राम)' : 'Sample weight (g)';
  String get aia => hi ? 'AIA % (यदि लैब जाँच हुई हो)' : 'AIA % (if lab tested)';
  String get tabTest => hi ? 'जाँच' : 'Test';
  String get tabResult => hi ? 'फैसला' : 'Verdict';
  String get tabKit => hi ? 'किट' : 'Kit';
  String get resultEmpty => hi ? 'जाँच चलाएँ। फैसला यहाँ दिखेगा।' : 'Run a test. The verdict will show here.';
  String get hear => hi ? 'सलाह सुनें' : 'Hear advice';
  String get why => hi ? 'कारण' : 'Why';
  String get also => hi ? 'यह भी ध्यान दें' : 'Also noted';
  String get ration => hi ? 'आज इसका उपयोग कैसे करें' : 'How to use it today';
  String get sensor => hi ? 'सेंसर जाँचें' : 'Check your sensors';
  String get cp => hi ? 'क्रूड प्रोटीन % DM' : 'Crude protein % DM';
  String get asfed => hi ? 'CP जैसा खिलाया %' : 'CP as-fed %';
  String get method => hi ? 'विधि' : 'Method';
  String get dm => hi ? 'शुष्क पदार्थ %' : 'Dry matter %';
  String get flieg => hi ? 'Flieg अंक' : 'Flieg score';
  String get ureaEst => hi ? 'यूरिया ग्रा/किग्रा' : 'Urea g/kg (screen)';
  String get chip => hi ? 'रंग चिप' : 'Colour chip';
  String get kitLead => hi
      ? 'फैसला इसी फ़ोन पर है। बोर्ड केवल नमी, pH और रंग मापता है।'
      : 'The verdict is on this phone. The board only measures moisture, pH and colour.';
  String get kitPacked => hi ? 'ऑफ़लाइन पैक' : 'Offline pack';
  String get none => '—';
  String get af => hi ? 'AFB1 जोखिम (पुराना आँकड़ा)' : 'AFB1 risk (historical)';
  String get higher => hi ? 'ऊँचा' : 'higher';
  String get lower => hi ? 'कम / अज्ञात' : 'lower / unknown';
  String get offlineNote => hi
      ? 'अज्ञात नाम कीवर्ड वर्ग से चलते हैं, ExtraTrees से नहीं। फफूंद रंग-जाँच है, CNN नहीं। AS7265x प्रोटीन नहीं। मॉडल फ़ोन पर हैं, बोर्ड पर नहीं।'
      : 'Unknown names use a keyword class, not ExtraTrees. Mould is a colour screen, not the CNN. AS7265x is not protein. Models stay on the phone, not the board.';
}
