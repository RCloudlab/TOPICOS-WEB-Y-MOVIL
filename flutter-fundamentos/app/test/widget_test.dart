import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:fundamentos_flutter/main.dart';
import 'package:fundamentos_flutter/pantallas.dart';

void main() {
  testWidgets('el menú muestra las prácticas', (tester) async {
    await tester.pumpWidget(const AppFundamentos());
    expect(find.text('Fundamentos de Flutter'), findsOneWidget);
    expect(find.text('StatefulWidget: contador'), findsOneWidget);
  });

  testWidgets('el contador sube con setState', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: PantallaContador()));
    expect(find.text('0'), findsOneWidget);
    await tester.tap(find.text('Agregar balón'));
    await tester.pump();
    expect(find.text('1'), findsOneWidget);
  });

  testWidgets('Row sin Expanded desborda y con Expanded no', (tester) async {
    tester.view.physicalSize = const Size(540, 900);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);

    await tester.pumpWidget(const MaterialApp(home: PantallaFila(conExpanded: false)));
    final error = tester.takeException();
    expect(error, isA<FlutterError>());
    // ignore: avoid_print
    print('SIN Expanded -> ${error.toString().split('\n').first}');

    await tester.pumpWidget(const MaterialApp(home: PantallaFila(conExpanded: true)));
    expect(tester.takeException(), isNull);
  });
}
