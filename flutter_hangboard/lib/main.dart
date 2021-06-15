import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:ui';
import 'package:flutter/rendering.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'dart:convert';
//import 'package:provider/provider.dart';

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

// TODO:  https://pub.dev/packages/audioplayers/example
class MyHomePage extends StatefulWidget {
  MyHomePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final TextEditingController _controller = TextEditingController();

  var ip_testboard = "ws://10.101.40.81:4321";
  var ip_zlagboard = "ws://10.101.40.40:4321";
  var ip_localhost = "ws://127.0.0.1:4321";

  final _channel = WebSocketChannel.connect(
    Uri.parse('ws://10.101.40.40:4321'),
  );

  _playLocal() async {
    AudioPlayer audioPlayer = AudioPlayer();
    //AudioCache audioCache = AudioCache(); // TODO: implement for iOS
    await audioPlayer.play("images/done.mp3", isLocal: true);
  }

  void _sendMessage() {
    // FIXME: Implement with parameters
    if (_controller.text.isNotEmpty) {
      _channel.sink.add(_controller.text);
    }
    _playLocal();
    _channel.sink.add("Start"); // FIXME
  }

  void _sendMessageStart() {
    _channel.sink.add("Start"); // FIXME
  }

  void _sendMessageStop() {
    _channel.sink.add("Stop"); // FIXME
  }

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
  void dispose() {
    _channel.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Column(
        children: [
          //titleSection,
          StreamBuilder(
            stream: _channel.stream,
            builder: (context, snapshot) {
              var testchen = "Nix";
              var LeftHold = "";
              var RightHold = "";
              double Rest = 0.0;
              var Exercise = "";
              var ExerciseType = "";
              var Counter = 0.0;
              var CurrentCounter = 0.0;
              double Completed = 0.0;
              var HangChangeDetected = "";
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
              }
              //return Text(snapshot.hasData ? '${snapshot.data}' : '');
              //return Text("Left " + left + " Right " + right);
              var imagename = 'images/zlagboard_evo.png'; // FIXME
              if (LeftHold != "") {
                imagename = 'images/zlagboard_evo.' +
                    LeftHold +
                    '.' +
                    RightHold +
                    '.png';
              }

              if (Rest == 10) {
                // TODO: Implement
                _playLocal();
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
                                'Hang detected: ' + HangState,
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
                ],
              ));
            },
          ),
          MyStatefulWidget(),
          //BoardSelection,
          //origSection,
        ],
      ),
      /*floatingActionButton: FloatingActionButton(
            onPressed: _sendMessage, //_incrementCounter,
            tooltip: 'Send a Command to Backend',
            child: Icon(Icons.send))*/
    );
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
