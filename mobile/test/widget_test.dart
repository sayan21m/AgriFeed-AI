import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:smartfeed_app/main.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('shows farmer tabs', (tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(const SmartFeedApp());
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 50));
    expect(find.text('AgriFeed-AI'), findsOneWidget);
    expect(find.text('Test'), findsWidgets);
    expect(find.text('Verdict'), findsOneWidget);
    expect(find.text('Kit'), findsWidgets);
    expect(find.text('Connect'), findsOneWidget);
    expect(find.textContaining('192.168'), findsNothing);
  });
}
