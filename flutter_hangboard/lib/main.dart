import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:ui';
import 'package:flutter/rendering.dart';
import 'dart:convert';
//import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:wakelock/wakelock.dart';

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
      home: MyHomePage(title: 'Hangboard'),
    );
  }
}

// ignore: todo
// TODO:  https://pub.dev/packages/audioplayers/example
class MyHomePage extends StatefulWidget {
  MyHomePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  Widget BoardSelection1 = Container(
      /* decoration: BoxDecoration( // does not load yet
          image: DecorationImage(
              image: AssetImage(
        "images/background.jpg",
      ))),*/
      child: Row(
    children: [
      Expanded(
          child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
              child: Text(
            "Testchen",
          ))
        ],
      ))
    ],
  ));

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      /* appBar: AppBar(
        title: Text(widget.title),
      ),*/
      body: Column(
        children: [
          ExerciseStatus(),
          // MyStatefulWidget(),
          // LineChartSample2(),

          //BoardSelection,
        ],
      ),
    );
  }
}

class ExerciseStatus extends StatefulWidget {
  const ExerciseStatus({Key? key}) : super(key: key);

  @override
  _ExerciseStatusState createState() => _ExerciseStatusState();
}

final String ip_zlagboard = "ws://10.101.40.40:4321";
final String ip_testboard = "ws://10.101.40.81:4321";
final String ip_localhost = "ws://127.0.0.1:4321";

class _ExerciseStatusState extends State<ExerciseStatus> {
  final _channel = WebSocketChannel.connect(
    Uri.parse(ip_localhost),
  );

  _playLocal() async {
    //AudioPlayer audioPlayer = AudioPlayer();
    // ignore: todo
    //AudioCache audioCache = AudioCache(); // TODO: implement for iOS
    await audioPlayer.play("images/done.mp3", isLocal: true);
  }

  AudioPlayer audioPlayer = AudioPlayer();

// FIXME

  _playSFX10() async {
    await audioPlayer.play("images/10.mp3", isLocal: true);
  }

  _playSFX9() async {
    await audioPlayer.play("images/9.mp3", isLocal: true);
  }

  _playSFX8() async {
    await audioPlayer.play("images/8.mp3", isLocal: true);
  }

  _playSFX7() async {
    await audioPlayer.play("images/7.mp3", isLocal: true);
  }

  _playSFX6() async {
    await audioPlayer.play("images/6.mp3", isLocal: true);
  }

  _playSFX5() async {
    await audioPlayer.play("images/5.mp3", isLocal: true);
  }

  _playSFX4() async {
    await audioPlayer.play("images/4.mp3", isLocal: true);
  }

  _playSFX3() async {
    await audioPlayer.play("images/3.mp3", isLocal: true);
  }

  _playSFX2() async {
    await audioPlayer.play("images/2.mp3", isLocal: true);
  }

  _playSFX1() async {
    await audioPlayer.play("images/1.mp3", isLocal: true);
  }

  _playSFXDone() async {
    await audioPlayer.play("images/done.mp3", isLocal: true);
  }

  void _sendMessage() {
    // FIXME: Implement with parameters

    _playLocal();
    _channel.sink.add("Start"); // FIXME
  }

  void _sendMessageStart() {
    _channel.sink.add("Start"); // FIXME
  }

  void _sendMessageStop() {
    _channel.sink.add("Stop"); // FIXME
  }

  List<Color> gradientColors = [
    // https://api.flutter.dev/flutter/dart-ui/Color-class.html
    const Color.fromRGBO(0, 0, 200, 0.4),
    const Color.fromRGBO(200, 0, 0, 1.0),
    //const Color(0xff0000ee),
    //const Color(0x0000ffff),
  ];

  var connection = false;

  @override
  Widget build(BuildContext context) {
    return Container(
      child: StreamBuilder(
        stream: _channel.stream,
        builder: (context, snapshot) {
          var testchen = "Nix";
          var LeftHold = "";
          var RightHold = "";
          double Rest = 0.0;
          var Exercise = "";
          // ignore: unused_local_variable
          var ExerciseType = "";
          // ignore: unused_local_variable
          var Counter = 0.0;
          // ignore: unused_local_variable
          var CurrentCounter = 0.0;
          double Completed = 0.0;
          double LoadLoss = 0.0; // FIXME
          // ignore: unused_local_variable
          var HangChangeDetected = "";
          var mytimes;
          var myload;
          List<FlSpot> mydata = [];
          bool HangDetected = false;
          if (snapshot.hasData) {
            testchen = snapshot.data.toString();

            connection = true; // If data received - connected
            Wakelock.enable(); // Stay awake, once data has been received

            Map<String, dynamic> ok1 = jsonDecode(testchen);
            if (ok1.containsKey("Left")) {
              LeftHold = ok1['Left'];
            }
            if (ok1.containsKey("Right")) {
              RightHold = ok1['Right'];
            }

            if (ok1.containsKey("Rest")) {
              if (ok1['Rest'] != 0) {
                Rest = double.parse(ok1['Rest']);
              } else {
                Rest = 0;
              }
            }
            if (ok1.containsKey("Counter")) {
              if (ok1['Counter'] != 0) {
                Counter = double.parse(ok1['Counter']);
              } else {
                Counter = 0;
              }
            }
            if (ok1.containsKey("CurrentCounter")) {
              if (ok1['CurrentCounter'] != 0) {
                CurrentCounter = double.parse(ok1['CurrentCounter']);
              } else {
                CurrentCounter = 0;
              }
            }

            if (ok1.containsKey("Completed")) {
              if (ok1['Completed'] != 0) {
                Completed = double.parse(ok1['Completed']);
              } else {
                Completed = 0;
              }
            }

            if (ok1.containsKey(("Exercise"))) {
              Exercise = ok1['Exercise'];
            }

            if (ok1.containsKey(("HangDetected"))) {
              HangDetected = ok1['HangDetected'];
            }

            if (ok1.containsKey("CurrentMeasurementsSeries")) {
              if (ok1["CurrentMeasurementsSeries"].containsKey("time")) {
                mytimes = ok1["CurrentMeasurementsSeries"]["time"];
                myload = ok1["CurrentMeasurementsSeries"]["load"];
                if (mytimes.length > 2) {
                  double t0 = double.parse(mytimes[0].toString());
                  for (int i = 0; i < mytimes.length; i++) {
                    mydata.add(FlSpot(
                      double.parse(mytimes[i].toString()) - t0,
                      double.parse(myload[i].toString()),
                    ));
                  }
                }
              }
            }
          }
          var imagename = 'images/zlagboard_evo.png'; // FIXME
          if (LeftHold != "") {
            imagename =
                'images/zlagboard_evo.' + LeftHold + '.' + RightHold + '.png';
          }

          // FIXME

          if (Rest == 10) {
            _playSFX10();
          }

          if (Rest == 9) {
            _playSFX9();
          }
          if (Rest == 8) {
            _playSFX8();
          }

          if (Rest == 7) {
            _playSFX7();
          }
          if (Rest == 6) {
            _playSFX6();
          }
          if (Rest == 5) {
            _playSFX5();
          }
          if (Rest == 4) {
            _playSFX4();
          }
          if (Rest == 3) {
            _playSFX3();
          }

          if (Rest == 2) {
            _playSFX2();
          }
          if (Rest == 1) {
            _playSFX1();
          }

          if (Rest == 0) {
            //    _playSFXDone();//FIXME - on start
          }

          var HangState = "no";
          if (HangDetected == true) {
            HangState = "yes";
          }

          return (Column(
            children: [
              Image.asset(imagename, fit: BoxFit.cover, width: 500),
              LinearProgressIndicator(
                value: Completed / 100,
                semanticsLabel: 'Linear progress indicator',
              ),
              Container(
                padding: const EdgeInsets.all(32),
                child: Row(
                  children: [
                    Expanded(
                      /*1*/
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          /*2*/
                          Container(
                            padding: const EdgeInsets.only(bottom: 8),
                            child: Text(
                              "Exercise: " + Exercise,
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          Text(
                            'Hang detected: ' +
                                HangState +
                                " with LoadLoss " +
                                LoadLoss.toString(),
                            style: TextStyle(
                              color: Colors.grey[500],
                            ),
                          ),
                        ],
                      ),
                    ),
                    /*3*/
                    Icon(
                      Icons.alarm,
                      color: Colors.red[500],
                    ),
                    Text(CurrentCounter.toString() +
                        "/" +
                        Counter.toString() +
                        "   Rest: " +
                        Rest.toString()),
                  ],
                ),
              ),
              Row(children: [
                Text("Controls: "),
                FloatingActionButton(
                    onPressed: _sendMessageStart,
                    child: Icon(Icons
                        .play_arrow)), // https://fonts.google.com/icons?selected=Material+Icons+Outlined:play_arrow

                FloatingActionButton(
                    onPressed: _sendMessageStop, // FIXME: implement a pause
                    child: Icon(Icons.do_not_touch)),
                FloatingActionButton(
                    onPressed: _sendMessageStop, child: Icon(Icons.stop)),
                FloatingActionButton(
                    onPressed: _sendMessage, // FIXME: implement
                    child: Icon(Icons.restart_alt)),
                FloatingActionButton(
                    onPressed: _sendMessage, // FIXME: state, not button
                    child: connection == true
                        ? Icon(Icons.wifi)
                        : Icon(Icons.wifi_off)),
              ]),
              Row(children: [
                mydata.length < 3
                    ? Text("No Hang - No Load")
                    : Expanded(
                        flex: 3,
                        child: 1 == 0
                            ? Text("ja")
                            : Stack(
                                children: <Widget>[
                                  AspectRatio(
                                    aspectRatio: 5,
                                    child: Container(
                                      child: Padding(
                                        padding: const EdgeInsets.only(
                                            right: 0.0,
                                            left: 0.0,
                                            top: 0,
                                            bottom: 0),
                                        child: LineChart(
                                          LineChartData(
                                            gridData: FlGridData(
                                              // Grid
                                              show: true,
                                              drawVerticalLine: true,
                                              getDrawingHorizontalLine:
                                                  (value) {
                                                // Grid Horizontal
                                                return FlLine(
                                                  color:
                                                      const Color(0xff37434d),
                                                  strokeWidth: 1,
                                                );
                                              },
                                              getDrawingVerticalLine: (value) {
                                                // Grid Vertical
                                                return FlLine(
                                                  color:
                                                      const Color(0xff37434d),
                                                  strokeWidth: 1,
                                                );
                                              },
                                            ),
                                            titlesData: FlTitlesData(
                                              // X Axis
                                              show: true,
                                              bottomTitles: SideTitles(
                                                showTitles: true,
                                                reservedSize: 22,
                                                getTextStyles: (value) =>
                                                    const TextStyle(
                                                        color:
                                                            Color(0xff68737d),
                                                        fontWeight:
                                                            FontWeight.bold,
                                                        fontSize: 16),
                                                getTitles: (value) {
                                                  // X Axis description

                                                  return value.toString(); //'';
                                                },
                                                margin: 8,
                                              ),
                                              leftTitles: SideTitles(
                                                // Y Axis
                                                showTitles: true,
                                                getTextStyles: (value) =>
                                                    const TextStyle(
                                                  color: Color(0xff67727d),
                                                  fontWeight: FontWeight.bold,
                                                  fontSize: 15,
                                                ),
                                                getTitles: (value) {
                                                  switch (value.toInt()) {
                                                    case 10:
                                                      return '10';
                                                    case 20:
                                                      return '20';
                                                    case 30:
                                                      return '30';
                                                    case 40:
                                                      return '40';
                                                    case 50:
                                                      return '50';
                                                    case 60:
                                                      return '60';
                                                    case 70:
                                                      return '70';
                                                    case 80:
                                                      return '80';
                                                    case 90:
                                                      return '90';
                                                  }
                                                  return '';
                                                },
                                                reservedSize: 28,
                                                margin: 12,
                                              ),
                                            ),
                                            borderData: FlBorderData(
                                                show: true,
                                                border: Border.all(
                                                    color:
                                                        const Color(0xff37434d),
                                                    width: 1)),
                                            //minX: 0, // Define extrema if needed
                                            //maxX: 10,
                                            minY: 0,
                                            maxY: 90,

                                            lineBarsData: [
                                              LineChartBarData(
                                                spots: mydata,
                                                //isCurved: true,
                                                colors: gradientColors,
                                                barWidth: 5,
                                                //  isStrokeCapRound: true,
                                                dotData: FlDotData(
                                                  show: false,
                                                ),
                                                belowBarData: BarAreaData(
                                                  show: true,
                                                  colors: gradientColors
                                                      .map((color) => color
                                                          .withOpacity(0.3))
                                                      .toList(),
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                      )
              ])
            ],
          ));
        },
      ),
    );
  }

  @override
  void dispose() {
    _channel.sink.close();
    super.dispose();
  }
}

/// This is the stateful widget that the main application instantiates.
class MyStatefulWidget extends StatefulWidget {
  const MyStatefulWidget({Key? key}) : super(key: key);

  @override
  State<MyStatefulWidget> createState() => _MyStatefulWidgetState();
}

/// This is the private State class that goes with MyStatefulWidget.
class _MyStatefulWidgetState extends State<MyStatefulWidget> {
  String dropdownValue = 'Localhost';

  @override
  Widget build(BuildContext context) {
    return DropdownButton<String>(
      value: dropdownValue,
      icon: const Icon(Icons.arrow_downward),
      iconSize: 24,
      elevation: 16,
      style: const TextStyle(color: Colors.deepPurple),
      underline: Container(
        height: 2,
        color: Colors.deepPurpleAccent,
      ),
      onChanged: (String? newValue) {
        setState(() {
          dropdownValue = newValue!;
        });
      },
      items: <String>['Localhost', 'Zlagboard']
          .map<DropdownMenuItem<String>>((String value) {
        return DropdownMenuItem<String>(
          value: value,
          child: Text(value),
        );
      }).toList(),
    );
  }
}
