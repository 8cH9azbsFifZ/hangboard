import 'dart:async';
//import 'dart:html';
import 'dart:io';
import 'package:audioplayers/audioplayers.dart';
//import 'package:audioplayers/audio_cache.dart';
import 'package:flutter/foundation.dart';

import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
//import 'dart:io' show Platform; //at the top

import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';

import 'package:flutter_svg/avd.dart';
import 'package:flutter_svg/flutter_svg.dart';

//final String assetName = 'assets/board.svg';
//SvgPicture.asset("images/board.svg");

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

// https://pub.dev/packages/audioplayers/example

class MyHomePage extends StatefulWidget {
  MyHomePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final TextEditingController _controller = TextEditingController();

  final _channel = WebSocketChannel.connect(
    //Uri.parse('wss://echo.websocket.org'),
    Uri.parse('ws://127.0.0.1:4321'),
  );

  //bool isIOS = Theme.of(context).platform == TargetPlatform.iOS;
  //String os = dio.Platform.operatingSystem; //in your code

  //dio.isIOS

  _playLocal() async {
    AudioPlayer audioPlayer = AudioPlayer();
    AudioCache audioCache = AudioCache();

    int result = await audioPlayer.play("images/done.mp3", isLocal: true);

    /*int result = await audioPlayer.play(
        "https://luan.xyz/files/audio/nasa_on_a_mission.mp3",
        isLocal: false);
  */
  }

  int _counter = 0;

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
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
          StreamBuilder(
            //stream: _channel.stream,
            builder: (context, snapshot) {
              return Text(snapshot.hasData ? '${snapshot.data}' : '');
            },
          )
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
            /*
            Image.asset(
              'images/board.png',
              fit: BoxFit.cover,
              //width: 500,
            ),
            */

            SvgPicture.asset('images/zlagboard_evo.svg'),
            titleSection,
            BoardSelection,
            origSection,
            StreamBuilder(
              stream: _channel.stream,
              builder: (context, snapshot) {
                return Text(snapshot.hasData ? '${snapshot.data}' : '');
              },
            )
          ],
        ),
        floatingActionButton: FloatingActionButton(
            onPressed: _sendMessage, //_incrementCounter,
            tooltip: 'Send a Command to Backend',
            child: Icon(Icons.send)));
  }
}

/*
    Text(
              '$_counter',
              style: Theme.of(context).textTheme.headline4,
            ),




*/
