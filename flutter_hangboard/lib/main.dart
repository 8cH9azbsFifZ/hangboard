import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:ui';
import 'package:flutter/rendering.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'dart:convert';

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

  final _channel = WebSocketChannel.connect(
    Uri.parse('ws://127.0.0.1:4321'),
  );

  _playLocal() async {
    AudioPlayer audioPlayer = AudioPlayer();
    //AudioCache audioCache = AudioCache(); // TODO: implement for iOS

    await audioPlayer.play("images/done.mp3", isLocal: true);
  }

  void _sendMessage() {
    if (_controller.text.isNotEmpty) {
      _channel.sink.add(_controller.text);
    }
    _playLocal();
    _channel.sink.add("Start"); // FIXME
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
          Icons.star,
          color: Colors.red[500],
        ),
        Text('41'),
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

  Widget BoardSelection = Container(
      child: Row(
    children: [
      Expanded(
          child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
              child: DropdownButton<String>(
            items: <String>[
              'Zlagboard EVO',
              'Zlagboard Mini',
              'Linebreaker Basis',
              'Beastmaker 1000'
            ].map((String value) {
              return DropdownMenuItem<String>(
                value: value,
                child: new Text(value),
              );
            }).toList(),
            onChanged: (_) {},
          ))
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
            titleSection,
            StreamBuilder(
              stream: _channel.stream,
              builder: (context, snapshot) {
                var testchen = "Nix";
                var left = "";
                var right = "";
                var rest = 0.0;
                if (snapshot.hasData) {
                  testchen = snapshot.data.toString();
                  Map<String, dynamic> ok1 = jsonDecode(testchen);
                  left = ok1['Left'];
                  right = ok1['Right'];
                  rest = double.parse(ok1['Rest']);
                }
                //return Text(snapshot.hasData ? '${snapshot.data}' : '');
                //return Text("Left " + left + " Right " + right);
                var imagename = 'images/zlagboard_evo.png';
                if (left != "") {
                  imagename =
                      'images/zlagboard_evo.' + left + '.' + right + '.png';
                }
                return (Column(
                  children: [
                    Image.asset(imagename, fit: BoxFit.cover, width: 500),
                    Text("Rest: " + rest.toString())
                  ],
                ));
              },
            ),
            BoardSelection,
            origSection,
          ],
        ),
        floatingActionButton: FloatingActionButton(
            onPressed: _sendMessage, //_incrementCounter,
            tooltip: 'Send a Command to Backend',
            child: Icon(Icons.send)));
  }
}
