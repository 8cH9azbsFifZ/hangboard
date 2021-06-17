import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:ui';
import 'package:flutter/rendering.dart';
import 'dart:convert';
//import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';

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
  Widget titleSection = Container(
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
                  'Hang for 10 seconds',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Text(
                'This is my workout',
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
        Text('41 of 80'),
      ],
    ),
  );

  Widget origSection = Container(
      child: Row(
    children: [
      Expanded(
          child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Form(
            child: TextFormField(
              //controller: _controller,
              decoration: InputDecoration(labelText: 'Send a message'),
            ),
          ),
          SizedBox(height: 24),
        ],
      ))
    ],
  ));

  Widget BoardSelection1 = Container(
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
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Column(
        children: [
          //titleSection,
          ExerciseStatus(),
          MyStatefulWidget(),
          LineChartSample2(),

          //BoardSelection,
          //origSection,
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

class _ExerciseStatusState extends State<ExerciseStatus> {
  var ip_testboard = "ws://10.101.40.81:4321";
  var ip_zlagboard = "ws://10.101.40.40:4321";
  var ip_localhost = "ws://127.0.0.1:4321";

  final _channel = WebSocketChannel.connect(
    Uri.parse('ws://10.101.40.40:4321'),
  );

  _playLocal() async {
    AudioPlayer audioPlayer = AudioPlayer();
    // ignore: todo
    //AudioCache audioCache = AudioCache(); // TODO: implement for iOS
    await audioPlayer.play("images/done.mp3", isLocal: true);
  }

/* // FIXME
  AudioPlayer audioPlayer = AudioPlayer();

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
*/
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
    const Color(0xff0000ee),
    const Color(0x0000ffff),
  ];
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
          String CurrentMeasurementsSeries = "";
          List<FlSpot> mydata = [];
          bool HangDetected = false;
          if (snapshot.hasData) {
            testchen = snapshot.data.toString();
            Map<String, dynamic> ok1 = jsonDecode(testchen);
            LeftHold = ok1['Left'];
            RightHold = ok1['Right'];

            if (ok1.containsKey("Rest")) {
              // FIXME safe detection
              if (ok1['Rest'] != 0) {
                Rest = double.parse(ok1['Rest']);
              } else {
                Rest = 0;
              }
            }

            if (ok1.containsKey("Completed")) {
              // FIXME safe detection
              if (ok1['Completed'] != 0) {
                Completed = double.parse(ok1['Completed']);
              } else {
                Completed = 0;
              }
            }

            Exercise = ok1['Exercise'];
            //ExerciseType = ok1['ExerciseType'];
            //Counter = double.parse(ok1['Counter']);
            //CurrentCounter = double.parse(ok1['CurrentCounter']);
            //Completed = double.parse(ok1['Completed']);
            //HangChangeDetected = ok1['HangChangeDetected'];
            HangDetected = ok1['HangDetected'];

            if (ok1.containsKey("CurrentMeasurementsSeries")) {
              //Map<String, dynamic> ok2 =
              //  jsonDecode(ok1["CurrentMeasurementsSeries"]);
              mytimes = ok1["CurrentMeasurementsSeries"]["time"];
              myload = ok1["CurrentMeasurementsSeries"]["load"];
              double t0 = double.parse(mytimes[0].toString());
              for (int i = 0; i < mytimes.length; i++) {
                mydata.add(FlSpot(
                  double.parse(mytimes[i].toString()) - t0,
                  double.parse(myload[i].toString()),
                )); //double.parse(mytimes[i]), double.parse(myload[i])));
              }
            }
          }
          //return Text(snapshot.hasData ? '${snapshot.data}' : '');
          //return Text("Left " + left + " Right " + right);
          var imagename = 'images/zlagboard_evo.png'; // FIXME
          if (LeftHold != "") {
            imagename =
                'images/zlagboard_evo.' + LeftHold + '.' + RightHold + '.png';
          }

          /* // FIXME

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
            //  _playSFXDone();
          }

          */
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
                    Text("Rest: " + Rest.toString()),
                  ],
                ),
              ),
              Row(children: [
                Text("Controls: "),
                FloatingActionButton(
                    onPressed: _sendMessageStart,
                    child: Icon(Icons.skateboarding)),
                FloatingActionButton(
                    onPressed: _sendMessageStop,
                    child: Icon(Icons.exit_to_app)),
                FloatingActionButton(
                    onPressed: _sendMessage, // FIXME: implement
                    child: Icon(Icons.restart_alt))
              ]),
              Row(children: [
                mydata.length == 0
                    ? Text("Tes1t")
                    : Column(
                        children: [
                          1 == 0
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
                                                getDrawingVerticalLine:
                                                    (value) {
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

                                                    return value
                                                        .toString(); //'';
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
                                                    //return value.toString();
                                                  },
                                                  reservedSize: 28,
                                                  margin: 12,
                                                ),
                                              ),
                                              borderData: FlBorderData(
                                                  show: true,
                                                  border: Border.all(
                                                      color: const Color(
                                                          0xff37434d),
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
                                )
                        ],
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

class LineChartSample2 extends StatefulWidget {
  @override
  _LineChartSample2State createState() => _LineChartSample2State();
}

class _LineChartSample2State extends State<LineChartSample2> {
  List<Color> gradientColors = [
    const Color(0xff0000ee),
    const Color(0x0000ffff),
  ];

  bool showAvg = false; // FIXME

  final _channel = WebSocketChannel.connect(
    // FIXME: global varible?
    Uri.parse('ws://10.101.40.40:4321'),
  );

  @override
  Widget build(BuildContext context) {
    return Container(
        child: StreamBuilder(
            stream: _channel.stream,
            builder: (context, snapshot) {
              var testchen = "Nix";
              var mytimes;
              var myload;
              // Code here
              String CurrentMeasurementsSeries = "";
              List<FlSpot> mydata = [];
              if (snapshot.hasData) {
                testchen = snapshot.data.toString();
                Map<String, dynamic> ok1 = jsonDecode(testchen);
                if (ok1.containsKey("CurrentMeasurementsSeries")) {
                  //Map<String, dynamic> ok2 =
                  //  jsonDecode(ok1["CurrentMeasurementsSeries"]);
                  mytimes = ok1["CurrentMeasurementsSeries"]["time"];
                  myload = ok1["CurrentMeasurementsSeries"]["load"];
                  double t0 = double.parse(mytimes[0].toString());
                  for (int i = 0; i < mytimes.length; i++) {
                    mydata.add(FlSpot(
                      double.parse(mytimes[i].toString()) - t0,
                      double.parse(myload[i].toString()),
                    )); //double.parse(mytimes[i]), double.parse(myload[i])));
                  }
                }

                /*
                CurrentMeasurementsSeries =
                    ok1['CurrentMeasurementsSeries'] != null
                        ? (ok1['CurrentMeasurementsSeries']).toString()
                        : "None";
                //   var SeriesTime = CurrentMeasurementsSeries['time'];
                //   var SeriesLoad = CurrentMeasurementsSeries['load'];
                var timesJson = jsonDecode(CurrentMeasurementsSeries)["time"];
                //   List<String> times =
                //    timesJson != null ? List.from(timesJson) : null;
                */
              }

/*
Example JSON to list
 String arrayText = '{"tags": ["dart", "flutter", "json"]}';

  var tagsJson = jsonDecode(arrayText)['tags'];
  List<String> tags = tagsJson != null ? List.from(tagsJson) : null;


*/

              /* Example data
              Workout(MainThread) server > Frame(fin=True, opcode=<Opcode.TEXT: 1>, 
              data=b'{"Exercise": "Hang", "Type": "Hang", "Left": "A1", "Right": "A7", "Counter": "10.00", "CurrentCounter": "1.20", 
              "Completed": "12", "Rest": "8.80", "HangChangeDetected": "", "HangDetected": true, 
              "FTI": 102.277591006134, "AverageLoad": 7.7173083760531505, "MaximalLoad": 8.356523627660334, "RFD": 3.9736694610795626,
               "LoadLoss": 0.01636598734691086, 
               "CurrentMeasurementsSeries": {"time": [1623957336.5194511, 1623957336.6248372, 1623957336.739917, 1623957336.8615391, 1623957336.9793222, 1623957337.08865, 1623957337.201374, 1623957337.310876, 1623957337.4224918, 1623957337.53201, 1623957337.6437378, 1623957337.753417, 1623957337.865253], "load": [6.372050120907403, 6.790819325251163, 6.943099035921621, 7.0280967457141665, 7.4415889303812275, 7.831522991491597, 8.19067443782122, 8.356523627660334, 8.35520437274116, 8.345906766644118, 8.215740281285541, 8.234021385165535, 8.219760867705883]}}', rsv1=False, rsv2=False, rsv3=False)

*/
/* Debugging receive
              String abd = "1324";
              abd = mytimes.toString();
              return (Text(abd));

              */
              if (mydata.length == 0) {
                return Text("No Hang");
              }

              return (Stack(
                children: <Widget>[
                  AspectRatio(
                    aspectRatio: 5,
                    child: Container(
                      child: Padding(
                        padding: const EdgeInsets.only(
                            right: 0.0, left: 0.0, top: 0, bottom: 0),
                        child: LineChart(
                          /* Old stuff
                          showAvg ? simData() : mainData(),
                          */

                          LineChartData(
                            gridData: FlGridData(
                              // Grid
                              show: true,
                              drawVerticalLine: true,
                              getDrawingHorizontalLine: (value) {
                                // Grid Horizontal
                                return FlLine(
                                  color: const Color(0xff37434d),
                                  strokeWidth: 1,
                                );
                              },
                              getDrawingVerticalLine: (value) {
                                // Grid Vertical
                                return FlLine(
                                  color: const Color(0xff37434d),
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
                                getTextStyles: (value) => const TextStyle(
                                    color: Color(0xff68737d),
                                    fontWeight: FontWeight.bold,
                                    fontSize: 16),
                                getTitles: (value) {
                                  // X Axis description
                                  /*
            switch (value.toInt()) {
              case 2:
                return 'MAR';
              case 5:
                return 'JUN';
              case 8:
                return 'SEP';
            }*/
                                  return value.toString(); //'';
                                },
                                margin: 8,
                              ),
                              leftTitles: SideTitles(
                                // Y Axis
                                showTitles: true,
                                getTextStyles: (value) => const TextStyle(
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
                                  //return value.toString();
                                },
                                reservedSize: 28,
                                margin: 12,
                              ),
                            ),
                            borderData: FlBorderData(
                                show: true,
                                border: Border.all(
                                    color: const Color(0xff37434d), width: 1)),
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
                                      .map((color) => color.withOpacity(0.3))
                                      .toList(),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                  SizedBox(
                    width: 60,
                    height: 34,
                    child: TextButton(
                      onPressed: () {
                        setState(() {
                          showAvg = !showAvg;
                        });
                      },
                      child: Text(
                        'avg',
                        style: TextStyle(
                            fontSize: 12,
                            color: showAvg
                                ? Colors.white.withOpacity(0.5)
                                : Colors.white),
                      ),
                    ),
                  ),
                ],
              ));
            }));
  }

  LineChartData mainData() {
    return LineChartData(
      gridData: FlGridData(
        // Grid
        show: true,
        drawVerticalLine: true,
        getDrawingHorizontalLine: (value) {
          // Grid Horizontal
          return FlLine(
            color: const Color(0xff37434d),
            strokeWidth: 1,
          );
        },
        getDrawingVerticalLine: (value) {
          // Grid Vertical
          return FlLine(
            color: const Color(0xff37434d),
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
          getTextStyles: (value) => const TextStyle(
              color: Color(0xff68737d),
              fontWeight: FontWeight.bold,
              fontSize: 16),
          getTitles: (value) {
            // X Axis description
            /*
            switch (value.toInt()) {
              case 2:
                return 'MAR';
              case 5:
                return 'JUN';
              case 8:
                return 'SEP';
            }*/
            return value.toString(); //'';
          },
          margin: 8,
        ),
        leftTitles: SideTitles(
          // Y Axis
          showTitles: true,
          getTextStyles: (value) => const TextStyle(
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
            //return value.toString();
          },
          reservedSize: 28,
          margin: 12,
        ),
      ),
      borderData: FlBorderData(
          show: true,
          border: Border.all(color: const Color(0xff37434d), width: 1)),
      //minX: 0, // Define extrema if needed
      //maxX: 10,
      minY: 0,
      maxY: 90,

      lineBarsData: [
        LineChartBarData(
          spots: [
            FlSpot(14.59, 2.46),
            FlSpot(14.67, 3.63),
            FlSpot(14.76, 5.90),
            FlSpot(14.85, 9.80),
            FlSpot(14.94, 15.94),
            FlSpot(15.03, 23.02),
            FlSpot(15.12, 29.22),
            FlSpot(15.20, 35.57),
            FlSpot(15.30, 41.35),
            FlSpot(15.38, 46.14),
            FlSpot(15.47, 51.14),
            FlSpot(15.56, 55.79),
            FlSpot(15.65, 58.96),
            FlSpot(15.73, 62.61),
            FlSpot(15.82, 67.10),
            FlSpot(15.91, 71.52),
            FlSpot(16.00, 74.99),
            FlSpot(16.08, 75.38),
            FlSpot(16.17, 74.36),
            FlSpot(16.26, 73.40),
            FlSpot(16.35, 72.63),
            FlSpot(16.44, 72.16),
            FlSpot(16.53, 72.15),
            FlSpot(16.61, 71.99),
            FlSpot(16.70, 71.80),
            FlSpot(16.79, 72.05),
            FlSpot(16.88, 72.37),
            FlSpot(16.96, 72.58),
            FlSpot(17.05, 72.99),
            FlSpot(17.14, 73.44),
            FlSpot(17.23, 73.69),
            FlSpot(17.31, 73.83),
            FlSpot(17.40, 73.75),
            FlSpot(17.49, 73.66),
            FlSpot(17.58, 73.96),
            FlSpot(17.67, 74.25),
            FlSpot(17.76, 74.12),
            FlSpot(17.84, 73.76),
            FlSpot(17.93, 73.48),
            FlSpot(18.02, 72.65),
            FlSpot(18.11, 70.01),
            FlSpot(18.19, 64.10),
            FlSpot(18.28, 51.73),
            FlSpot(18.37, 37.66),
            FlSpot(18.46, 26.44),
            FlSpot(18.55, 16.02),
            FlSpot(18.64, 9.02),
            FlSpot(18.72, 4.72),
            FlSpot(18.81, 2.04),
            FlSpot(22.89, 2.74),
            FlSpot(22.98, 4.59),
            FlSpot(23.07, 7.57),
          ],
          //isCurved: true,
          colors: gradientColors,
          barWidth: 5,
          //  isStrokeCapRound: true,
          dotData: FlDotData(
            show: false,
          ),
          belowBarData: BarAreaData(
            show: true,
            colors:
                gradientColors.map((color) => color.withOpacity(0.3)).toList(),
          ),
        ),
      ],
    );
  }

  LineChartData simData() {
    return LineChartData(
      gridData: FlGridData(
        // Grid
        show: true,
        drawVerticalLine: true,
        getDrawingHorizontalLine: (value) {
          // Grid Horizontal
          return FlLine(
            color: const Color(0xff37434d),
            strokeWidth: 1,
          );
        },
        getDrawingVerticalLine: (value) {
          // Grid Vertical
          return FlLine(
            color: const Color(0xff37434d),
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
          getTextStyles: (value) => const TextStyle(
              color: Color(0xff68737d),
              fontWeight: FontWeight.bold,
              fontSize: 16),
          getTitles: (value) {
            // X Axis description
            /*
            switch (value.toInt()) {
              case 2:
                return 'MAR';
              case 5:
                return 'JUN';
              case 8:
                return 'SEP';
            }*/
            return value.toString(); //'';
          },
          margin: 8,
        ),
        leftTitles: SideTitles(
          // Y Axis
          showTitles: true,
          getTextStyles: (value) => const TextStyle(
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
            //return value.toString();
          },
          reservedSize: 28,
          margin: 12,
        ),
      ),
      borderData: FlBorderData(
          show: true,
          border: Border.all(color: const Color(0xff37434d), width: 1)),
      //minX: 0, // Define extrema if needed
      //maxX: 10,
      minY: 0,
      maxY: 90,

      lineBarsData: [
        LineChartBarData(
          spots: [
            FlSpot(14.59, 2.46),
            FlSpot(14.67, 3.63),
            FlSpot(14.76, 5.90),
            FlSpot(14.85, 9.80),
            FlSpot(14.94, 15.94),
            FlSpot(15.03, 23.02),
            FlSpot(15.12, 29.22),
            FlSpot(15.20, 35.57),
            FlSpot(15.30, 41.35),
            FlSpot(15.38, 46.14),
            FlSpot(15.47, 51.14),
            FlSpot(15.56, 55.79),
            FlSpot(15.65, 58.96),
            FlSpot(15.73, 62.61),
            FlSpot(15.82, 67.10),
            FlSpot(15.91, 71.52),
            FlSpot(16.00, 74.99),
            FlSpot(16.08, 75.38),
            FlSpot(16.17, 74.36),
            FlSpot(16.26, 73.40),
            FlSpot(16.35, 72.63),
            FlSpot(16.44, 72.16),
            FlSpot(16.53, 72.15),
            FlSpot(16.61, 71.99),
            FlSpot(16.70, 71.80),
            FlSpot(16.79, 72.05),
            FlSpot(16.88, 72.37),
            FlSpot(16.96, 72.58),
            FlSpot(17.05, 72.99),
            FlSpot(17.14, 73.44),
            FlSpot(17.23, 73.69),
            FlSpot(17.31, 73.83),
            FlSpot(17.40, 73.75),
            FlSpot(17.49, 73.66),
            FlSpot(17.58, 73.96),
            FlSpot(17.67, 74.25),
            FlSpot(17.76, 74.12),
            FlSpot(17.84, 73.76),
            FlSpot(17.93, 73.48),
            FlSpot(18.02, 72.65),
            FlSpot(18.11, 70.01),
            FlSpot(18.19, 64.10),
            FlSpot(18.28, 51.73),
            FlSpot(18.37, 37.66),
            FlSpot(18.46, 26.44),
            FlSpot(18.55, 16.02),
            FlSpot(18.64, 9.02),
            FlSpot(18.72, 4.72),
            FlSpot(18.81, 2.04),
            FlSpot(22.89, 2.74),
            FlSpot(22.98, 4.59),
            FlSpot(23.07, 7.57),
          ],
          //isCurved: true,
          colors: gradientColors,
          barWidth: 5,
          //  isStrokeCapRound: true,
          dotData: FlDotData(
            show: false,
          ),
          belowBarData: BarAreaData(
            show: true,
            colors:
                gradientColors.map((color) => color.withOpacity(0.3)).toList(),
          ),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _channel.sink.close();
    super.dispose();
  }
}
