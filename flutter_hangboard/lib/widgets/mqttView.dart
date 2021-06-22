import 'dart:io' show Platform;
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_hangboard/mqtt/state/MQTTAppState.dart';
import 'package:flutter_hangboard/mqtt/MQTTManager.dart';

class MQTTView extends StatefulWidget {
  @override
  State<StatefulWidget> createState() {
    return _MQTTViewState();
  }
}

class _MQTTViewState extends State<MQTTView> {
  final TextEditingController _hostTextController = TextEditingController();
  final TextEditingController _messageTextController = TextEditingController();
  final TextEditingController _topicTextController = TextEditingController();
  late MQTTAppState currentAppState;
  late MQTTManager manager;

  @override
  void initState() {
    super.initState();

    /*
    _hostTextController.addListener(_printLatestValue);
    _messageTextController.addListener(_printLatestValue);
    _topicTextController.addListener(_printLatestValue);

     */
  }

  @override
  void dispose() {
    _hostTextController.dispose();
    _messageTextController.dispose();
    _topicTextController.dispose();
    super.dispose();
  }

  /*
  _printLatestValue() {
    print("Second text field: ${_hostTextController.text}");
    print("Second text field: ${_messageTextController.text}");
    print("Second text field: ${_topicTextController.text}");
  }

   */

  @override
  Widget build(BuildContext context) {
    final MQTTAppState appState = Provider.of<MQTTAppState>(context);
    // Keep a reference to the app state.
    currentAppState = appState;
    final Scaffold scaffold = Scaffold(body: _buildColumn());
    return scaffold;
  }

  // ignore: unused_element
  Widget _buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('MQTT'),
      backgroundColor: Colors.greenAccent,
    );
  }

  Widget _buildColumn() {
    return Column(
      children: <Widget>[
        _buildConnectionStateText(
            _prepareStateMessageFrom(currentAppState.getAppConnectionState)),
        _buildHangboardImage(currentAppState.getImageName),
        _buildEditableColumn(),
        _buildTimerStatus(currentAppState.getTimerDuration,
            currentAppState.getTimerElapsed, currentAppState.getTimerCompleted),
        _buildHoldStatus(
            currentAppState.getHoldLeft, currentAppState.getHoldRight),
        _buildExerciseType(currentAppState.getExerciseType),
        _buildControls(currentAppState.getAppConnectionState),
        _buildScrollableTextWith(currentAppState.getHistoryText)
      ],
    );
  }

  Widget _buildHangboardImage(String Imagename) {
    return Column(children: [
      Image.asset(Imagename, fit: BoxFit.cover, width: 500),
    ]);
  }
//

  Widget _buildEditableColumn() {
    return Padding(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        children: <Widget>[
          _buildTextFieldWith(_hostTextController, 'Enter broker address',
              currentAppState.getAppConnectionState),
          const SizedBox(height: 10),
          /*_buildTextFieldWith(
              _topicTextController,
              'Enter a topic to subscribe or listen',
              currentAppState.getAppConnectionState),
          const SizedBox(height: 10),*/
          _buildPublishMessageRow(),
          const SizedBox(height: 10),
          _buildConnecteButtonFrom(currentAppState.getAppConnectionState)
        ],
      ),
    );
  }

  Widget _buildPublishMessageRow() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: <Widget>[
        Expanded(
          child: _buildTextFieldWith(_messageTextController, 'Enter a command',
              currentAppState.getAppConnectionState),
        ),
        _buildSendButtonFrom(currentAppState.getAppConnectionState)
      ],
    );
  }

  Widget _buildConnectionStateText(String status) {
    return Row(
      children: <Widget>[
        Expanded(
          child: Container(
              color: Colors.deepOrangeAccent,
              child: Text(status, textAlign: TextAlign.center)),
        ),
      ],
    );
  }

  Widget _buildTextFieldWith(TextEditingController controller, String hintText,
      MQTTAppConnectionState state) {
    bool shouldEnable = false;
    if (controller == _messageTextController &&
        state == MQTTAppConnectionState.connected) {
      shouldEnable = true;
    } else if ((controller == _hostTextController &&
            state == MQTTAppConnectionState.disconnected) ||
        (controller == _topicTextController &&
            state == MQTTAppConnectionState.disconnected)) {
      shouldEnable = true;
    }
    return TextField(
        enabled: shouldEnable,
        controller: controller,
        decoration: InputDecoration(
          contentPadding:
              const EdgeInsets.only(left: 0, bottom: 0, top: 0, right: 0),
          labelText: hintText,
        ));
  }

  Widget _buildHoldStatus(String Left, String Right) {
    return Column(
      children: [Text("Left: " + Left + " - Right: " + Right)],
    );
  }

  Widget _buildExerciseType(String Exercise) {
    return Column(
      children: [Text("Exercise: " + Exercise)],
    );
  }

  Widget _buildTimerStatus(
      double TimerDuration, double TimerElapsed, double TimerCompleted) {
    return Column(
      children: [
        LinearProgressIndicator(
          value: TimerCompleted,
          semanticsLabel: 'Linear progress indicator',
        ),
        Text(TimerElapsed.toString() +
            " / " +
            TimerDuration.toString() +
            " - Completed: " +
            TimerCompleted.toString())
      ],
    );
  }

  Widget _buildControls(MQTTAppConnectionState state) {
    return Row(children: [
      Text("Controls: "),
      FloatingActionButton(
          onPressed: _sendMessageStart,
          child: Icon(Icons
              .play_arrow)), // https://fonts.google.com/icons?selected=Material+Icons+Outlined:play_arrow

      FloatingActionButton(
          onPressed: _sendMessagePause, // FIXME: implement a pause
          child: Icon(Icons.do_not_touch)),
      FloatingActionButton(
          onPressed: _sendMessageStop, child: Icon(Icons.stop)),
      FloatingActionButton(
          onPressed: _sendMessageStart, // FIXME: implement
          child: Icon(Icons.restart_alt)),
      FloatingActionButton(
          onPressed: _configureAndConnect, // FIXME: state, not button
          child: state == MQTTAppConnectionState.connected
              ? Icon(Icons.wifi)
              : Icon(Icons.wifi_off)),
    ]);
  }

  Widget _buildScrollableTextWith(String text) {
    return Padding(
      padding: const EdgeInsets.all(20.0),
      child: Container(
        width: 400,
        height: 200,
        child: SingleChildScrollView(
          child: Text(text),
        ),
      ),
    );
  }

  Widget _buildConnecteButtonFrom(MQTTAppConnectionState state) {
    return Row(
      children: <Widget>[
        Expanded(
          // ignore: deprecated_member_use
          child: RaisedButton(
            color: Colors.lightBlueAccent,
            child: const Text('Connect'),
            onPressed: state == MQTTAppConnectionState.disconnected
                ? _configureAndConnect
                : null, //
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          // ignore: deprecated_member_use
          child: RaisedButton(
            color: Colors.redAccent,
            child: const Text('Disconnect'),
            onPressed: state == MQTTAppConnectionState.connected
                ? _disconnect
                : null, //
          ),
        ),
      ],
    );
  }

  Widget _buildSendButtonFrom(MQTTAppConnectionState state) {
    // ignore: deprecated_member_use
    return RaisedButton(
      color: Colors.green,
      child: const Text('Send'),
      onPressed: state == MQTTAppConnectionState.connected
          ? () {
              _publishMessage(_messageTextController.text);
            }
          : null, //
    );
  }

  // Utility functions
  String _prepareStateMessageFrom(MQTTAppConnectionState state) {
    switch (state) {
      case MQTTAppConnectionState.connected:
        return 'Connected';
      case MQTTAppConnectionState.connecting:
        return 'Connecting';
      case MQTTAppConnectionState.disconnected:
        return 'Disconnected';
    }
  }

  void _configureAndConnect() {
    // ignore: flutter_style_todos
    // ignore: todo
    // TODO: Use UUID
    String osPrefix = 'Flutter_iOS'; // FIXME
    if (Platform.isAndroid) {
      osPrefix = 'Flutter_Android';
    }
    manager = MQTTManager(
        host: "localhost", //_hostTextController.text,
        topic: "hangboard/workout/timerstatus", //_topicTextController.text,
        identifier: osPrefix,
        state: currentAppState);
    manager.initializeMQTTClient();
    manager.connect();
  }

  void _disconnect() {
    manager.disconnect();
  }

  void _sendMessageStart() {
    _publishMessage("Start");
  }

  void _sendMessageStop() {
    _publishMessage("Stop");
  }

  void _sendMessagePause() {
    _publishMessage("Pause");
  }

  void _publishMessage(String text) {
    final String message = text;
    manager.publish_topic("hangboard/workout/control", message); // FIXME
    _messageTextController.clear();
  }
}
