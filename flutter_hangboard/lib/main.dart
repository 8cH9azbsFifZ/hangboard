import 'package:flutter/material.dart';
import 'package:flutter_hangboard/widgets/mqttView.dart';
import 'package:flutter_hangboard/mqtt/state/MQTTAppState.dart';
import 'package:provider/provider.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
        title: 'Hangboard',
        theme: ThemeData(
          primarySwatch: Colors.red,
        ),
        home: ChangeNotifierProvider<MQTTAppState>(
          create: (_) => MQTTAppState(),
          child: MQTTView(),
        )
        //(title: 'Hangboard')),
        );
  }
}
