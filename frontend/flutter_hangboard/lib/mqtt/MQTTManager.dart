import 'package:mqtt_client/mqtt_client.dart';
import 'package:flutter_hangboard/mqtt/state/MQTTAppState.dart';
import 'package:mqtt_client/mqtt_server_client.dart';
//import 'package:mqtt_client/mqtt_browser_client.dart';
//import 'package:flutter/foundation.dart' show kIsWeb;

class MQTTManager {
  // Private instance of client
  final MQTTAppState _currentState;

  //MqttBrowserClient? _client1;
  MqttServerClient? _client;

  final String _identifier;
  final String _host;
  final String _topic;

  // Constructor
  // ignore: sort_constructors_first
  MQTTManager(
      {required String host,
      required String topic,
      required String identifier,
      required MQTTAppState state})
      : _identifier = identifier,
        _host = host,
        _topic = topic,
        _currentState = state;

  void initializeMQTTClient() {
    /*if (kIsWeb) {
      // running on the web!
      _client1 = MqttBrowserClient('ws://hangboard', '');
      _client1!.keepAlivePeriod = 20;
      _client1!.port = 9001;
      _client1!.onDisconnected = onDisconnected;
      _client1!.onConnected = onConnected;
      _client1!.onSubscribed = onSubscribed;
      _client1!.logging(on: false);
    } else {*/
    // NOT running on the web! You can check for additional platforms here.
    _client = MqttServerClient(_host, _identifier);
    _client!.secure = false;
    _client!.port = 1883;
    _client!.keepAlivePeriod = 20;
    _client!.onDisconnected = onDisconnected;
    _client!.logging(on: false);

    /// Add the successful connection callback
    _client!.onConnected = onConnected;
    _client!.onSubscribed = onSubscribed;
    //}

    final MqttConnectMessage connMess = MqttConnectMessage()
        .withClientIdentifier(_identifier)
        .withWillTopic(
            'willtopic') // If you set this you must set a will message
        .withWillMessage('My Will message')
        .startClean() // Non persistent session for testing
        .withWillQos(MqttQos.atLeastOnce);
    print('EXAMPLE::Mosquitto client connecting....');
    _client!.connectionMessage = connMess;
  }

  // Connect to the host
  // ignore: avoid_void_async
  void connect() async {
    // if (kIsWeb) {
    //   assert(_client1 != null);
    // } else {
    assert(_client != null);
    // }
    try {
      print('EXAMPLE::Mosquitto start client connecting....');
      _currentState.setAppConnectionState(MQTTAppConnectionState.connecting);
      // if (kIsWeb) {
      //  await _client1!.connect();
      //} else {
      await _client!.connect();
//}
    } on Exception catch (e) {
      print('EXAMPLE::client exception - $e');
      disconnect();
    }
  }

  void disconnect() {
    print('Disconnected');
    // if (kIsWeb) {
    //  _client1!.disconnect();
    //} else {
    _client!.disconnect();
//}
  }

  void publish(String message) {
    final MqttClientPayloadBuilder builder = MqttClientPayloadBuilder();
    builder.addString(message);
    // if (kIsWeb) {
    //   _client1!.publishMessage(_topic, MqttQos.exactlyOnce, builder.payload!);
    // } else {
    _client!.publishMessage(_topic, MqttQos.exactlyOnce, builder.payload!);
    // }
  }

  void publish_topic(String topic, String message) {
    final MqttClientPayloadBuilder builder = MqttClientPayloadBuilder();
    builder.addString(message);
    //if (kIsWeb) {
    //  _client1!.publishMessage(topic, MqttQos.exactlyOnce, builder.payload!);
    //} else {
    _client!.publishMessage(topic, MqttQos.exactlyOnce, builder.payload!);
    //}
  }

  /// The subscribed callback
  void onSubscribed(String topic) {
    print('EXAMPLE::Subscription confirmed for topic $topic');
  }

  /// The unsolicited disconnect callback
  void onDisconnected() {
    print('EXAMPLE::OnDisconnected client callback - Client disconnection');
    //if (kIsWeb) {
    //  if (_client1!.connectionStatus!.returnCode ==
    //       MqttConnectReturnCode.noneSpecified) {
    //    print('EXAMPLE::OnDisconnected callback is solicited, this is correct');
    //   }
    //  } else {
    if (_client!.connectionStatus!.returnCode ==
        MqttConnectReturnCode.noneSpecified) {
      print('EXAMPLE::OnDisconnected callback is solicited, this is correct');
    }
    // }
    _currentState.setAppConnectionState(MQTTAppConnectionState.disconnected);
  }

  /// The successful connect callback
  void onConnected() {
    _currentState.setAppConnectionState(MQTTAppConnectionState.connected);
    print('EXAMPLE::Mosquitto client connected....');
    /* if (kIsWeb) {
      _client1!.subscribe(_topic, MqttQos.atLeastOnce); // FIXME
      _client1!
          .subscribe("hangboard/sensor/load/loadstatus", MqttQos.atMostOnce);
      _client1!.subscribe("hangboard/sensor/sensorstatus", MqttQos.exactlyOnce);
      _client1!.subscribe("hangboard/sensor/lastexercise", MqttQos.exactlyOnce);
      _client1!.subscribe("hangboard/workout/holds", MqttQos.atLeastOnce);
      _client1!
          .subscribe("hangboard/workout/exercisetype", MqttQos.atLeastOnce);
      _client1!.subscribe("hangboard/workout/workoutlist", MqttQos.atLeastOnce);
      _client1!
          .subscribe("hangboard/workout/workoutstatus", MqttQos.atLeastOnce);
      _client1!.updates!.listen((List<MqttReceivedMessage<MqttMessage?>>? c) {
        // ignore: avoid_as
        final MqttPublishMessage recMess = c![0].payload as MqttPublishMessage;

        // final MqttPublishMessage recMess = c![0].payload;
        final String pt =
            MqttPublishPayload.bytesToStringAsString(recMess.payload.message!);
        if (recMess.variableHeader!.topicName ==
            "hangboard/workout/timerstatus") {
          _currentState.setCurrentTimer(pt);
        }
        if (recMess.variableHeader!.topicName ==
            "hangboard/sensor/load/loadstatus") {
          _currentState.setLoadStatus(pt);
        }
        if (recMess.variableHeader!.topicName ==
            "hangboard/sensor/sensorstatus") {
          _currentState.setSensorStatus(pt);
        }
        if (recMess.variableHeader!.topicName ==
            "hangboard/workout/workoutstatus") {
          _currentState.setWorkoutStatus(pt);
        }
        if (recMess.variableHeader!.topicName ==
            "hangboard/sensor/lastexercise") {
          _currentState.setReceivedText(pt);

          _currentState.setLastExercise(pt);
        }
        if (recMess.variableHeader!.topicName == "hangboard/workout/holds") {
          _currentState.setCurrentHolds(pt);
        }
        if (recMess.variableHeader!.topicName ==
            "hangboard/workout/exercisetype") {
          _currentState.setExerciseType(pt);
        }
        if (recMess.variableHeader!.topicName ==
            "hangboard/workout/workoutlist") {
          _currentState.SetWorkoutList(pt);
        }

        // print(          'EXAMPLE::Change notification:: topic is <${c[0].topic}>, payload is <-- $pt -->');
        // print('');
      });
    } else {*/
    _client!.subscribe(_topic, MqttQos.atLeastOnce); // FIXME
    _client!.subscribe("hangboard/sensor/load/loadstatus", MqttQos.atMostOnce);
    _client!.subscribe("hangboard/sensor/sensorstatus", MqttQos.exactlyOnce);
    _client!.subscribe("hangboard/sensor/lastexercise", MqttQos.exactlyOnce);
    _client!.subscribe("hangboard/workout/holds", MqttQos.atLeastOnce);
    _client!.subscribe("hangboard/workout/exercisetype", MqttQos.atLeastOnce);
    _client!.subscribe("hangboard/workout/workoutlist", MqttQos.atLeastOnce);
    _client!.subscribe("hangboard/workout/workoutstatus", MqttQos.atLeastOnce);
    _client!.subscribe("hangboard/workout/setinfo", MqttQos.atLeastOnce);
    _client!.subscribe("hangboard/workout/userstatistics", MqttQos.atLeastOnce);
    _client!.subscribe("hangboard/workout/upcoming", MqttQos.atLeastOnce);
    _client!.updates!.listen((List<MqttReceivedMessage<MqttMessage?>>? c) {
      // ignore: avoid_as
      final MqttPublishMessage recMess = c![0].payload as MqttPublishMessage;

      // final MqttPublishMessage recMess = c![0].payload;
      final String pt =
          MqttPublishPayload.bytesToStringAsString(recMess.payload.message!);
      if (recMess.variableHeader!.topicName ==
          "hangboard/workout/timerstatus") {
        _currentState.setCurrentTimer(pt);
      }
      if (recMess.variableHeader!.topicName ==
          "hangboard/sensor/load/loadstatus") {
        _currentState.setLoadStatus(pt);
      }
      if (recMess.variableHeader!.topicName ==
          "hangboard/sensor/sensorstatus") {
        _currentState.setSensorStatus(pt);
      }
      if (recMess.variableHeader!.topicName == "hangboard/workout/setinfo") {
        _currentState.setSetInfo(pt);
      }
      if (recMess.variableHeader!.topicName ==
          "hangboard/workout/workoutstatus") {
        _currentState.setWorkoutStatus(pt);
      }
      if (recMess.variableHeader!.topicName == "hangboard/workout/upcoming") {
        _currentState.setUpcoming(pt);
      }
      if (recMess.variableHeader!.topicName ==
          "hangboard/sensor/lastexercise") {
        _currentState.setReceivedText(pt);

        _currentState.setLastExercise(pt);
      }
      if (recMess.variableHeader!.topicName == "hangboard/workout/holds") {
        _currentState.setCurrentHolds(pt);
      }
      if (recMess.variableHeader!.topicName ==
          "hangboard/workout/exercisetype") {
        _currentState.setExerciseType(pt);
      }
      if (recMess.variableHeader!.topicName ==
          "hangboard/workout/workoutlist") {
        _currentState.SetWorkoutList(pt);
      }
      if (recMess.variableHeader!.topicName ==
          "hangboard/workout/userstatistics") {
        _currentState.SetUserStatistics(pt);
      }
      // print(          'EXAMPLE::Change notification:: topic is <${c[0].topic}>, payload is <-- $pt -->');
      // print('');
    });
    // }
    //print(        'EXAMPLE::OnConnected client callback - Client connection was sucessful');
  }
}
