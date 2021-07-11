import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_hangboard/mqtt/state/MQTTAppState.dart';
import 'package:flutter_hangboard/mqtt/MQTTManager.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:assets_audio_player/assets_audio_player.dart';
import 'package:wakelock/wakelock.dart';
import 'package:percent_indicator/percent_indicator.dart';

class MQTTView extends StatefulWidget {
  @override
  State<StatefulWidget> createState() {
    return _MQTTViewState();
  }
}

// FIXME: Fix: Current Set information
// FIXME: Fix: HangDetected

// ignore: todo
// TODO: sound on hang and no hang

class _MQTTViewState extends State<MQTTView> {
  final TextEditingController _hostTextController = TextEditingController();
  final TextEditingController _messageTextController = TextEditingController();
  final TextEditingController _topicTextController = TextEditingController();
  late MQTTAppState currentAppState;
  late MQTTManager manager;

  AudioPlayer audioPlayer = AudioPlayer();
  final assetsAudioPlayer = AssetsAudioPlayer();
  final PlaySFX10 = AssetsAudioPlayer();

  @override
  void initState() {
    super.initState();
    PlaySFX10.open(Audio("images/10.mp3"), autoStart: false);
  }

  @override
  void dispose() {
    _hostTextController.dispose();
    _messageTextController.dispose();
    _topicTextController.dispose();
    super.dispose();
  }

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
        _buildScrollableTextWith(currentAppState.getHistoryText),
        _buildUpcomingSets(currentAppState.getUpcomingSets),
        _buildWorkoutSelector(
            currentAppState.getWorkoutName, currentAppState.GetWorkoutList),
        _buildHangboardImage(currentAppState.getImageName),
        _buildTimerStatus(
            currentAppState.getTimerDuration,
            currentAppState.getTimerElapsed,
            currentAppState.getTimerCompleted,
            currentAppState.getTimerCountdown,
            currentAppState.getTimerCurrentSet,
            currentAppState.getTimerTotalSets,
            currentAppState.getTimerCurrentRep,
            currentAppState.getTimerTotalReps),

        _buildExerciseType(currentAppState.getExerciseType),
        _buildIntensityPlot(
            currentAppState.getCurrentItensity,
            currentAppState.getCurrentSetIntensity,
            currentAppState.getCurrentIntensityTooHigh),
        _buildControls(currentAppState.getAppConnectionState),
        //_buildLoadPlot(currentAppState.getLoadCurrentData),
        _buildLoadPlotDisplay(currentAppState.getLoadCurrent),
        _buildLastExerciseStatistics(currentAppState.getLastHangTime,
            currentAppState.getLastMaximalLoad),
      ],
    );
  }

  Widget _buildUpcomingSets(String UpcomingSets) {
    return (Text(UpcomingSets));
  }

  Widget _buildIntensityPlot(double CurrentItensity, double CurrentSetIntensity,
      bool CurrentIntensityTooHigh) {
    double RelativeCurrentIntensity = 0.0;
    if (CurrentSetIntensity > 0) {
      RelativeCurrentIntensity = CurrentItensity / CurrentSetIntensity;
    }

    if (CurrentIntensityTooHigh) {
      _playSFX("images/warn.mp3"); // FIXME: make configurable
    }

    Color _barcolor = Colors.black;
    if (CurrentItensity < 0) {
      CurrentItensity = 0.0;
    }
    if (CurrentItensity < 0.5) {
      _barcolor = Colors.blueAccent;
    } else if (CurrentItensity < 0.7) {
      _barcolor = Colors.greenAccent;
    } else if (CurrentItensity < 0.9) {
      _barcolor = Colors.yellowAccent;
    } else {
      _barcolor = Colors.redAccent;
    }
    if (CurrentItensity > 1.0) {
      CurrentItensity = 1.0;
    }

    return (Column(
      children: [
        LinearPercentIndicator(
          percent: CurrentItensity,
          center: new Text(
            CurrentItensity.toStringAsFixed(2),
            style: new TextStyle(fontWeight: FontWeight.bold, fontSize: 20.0),
          ),
          //footer:
          leading: new Text(
            "Intensity",
            style: new TextStyle(fontWeight: FontWeight.bold, fontSize: 17.0),
          ),
          progressColor: _barcolor,
        ),
        (CurrentSetIntensity < CurrentItensity)
            ? Text(
                "Current Intensity " +
                    CurrentItensity.toStringAsFixed(1) +
                    " and Exercise Int " +
                    CurrentSetIntensity.toStringAsFixed(1),
                style: TextStyle(color: Colors.redAccent))
            : LinearPercentIndicator(
                percent: RelativeCurrentIntensity,
                center: new Text(
                  RelativeCurrentIntensity.toStringAsFixed(2),
                  style: new TextStyle(
                      fontWeight: FontWeight.bold, fontSize: 20.0),
                ),
                //footer:
                leading: new Text(
                  "Relative Intensity",
                  style: new TextStyle(
                      fontWeight: FontWeight.bold, fontSize: 17.0),
                ),
                progressColor: _barcolor,
              )
      ],
    ));
  }

  Widget _buildLastExerciseStatistics(
      double LastHangTime, double LastMaximalLoad) {
    return (Text("Last Exercise: " +
        LastHangTime.toString() +
        "s with " +
        LastMaximalLoad.toString() +
        "kg"));
  }

  // ignore: unused_element
  Widget _buildExerciseDescription(
      String Imagename, String ExerciseDescription) {
    return Column(children: [
      Image.asset(Imagename, fit: BoxFit.cover, width: 500),
      Text(ExerciseDescription)
    ]);
  }

  Widget _buildHangboardImage(String Imagename) {
    return Column(children: [
      Image.asset(Imagename, fit: BoxFit.cover, width: 500),
    ]);
  }

  // ignore: unused_element
  Widget _buildLoadPlotDisplay(double LoadCurrent) {
    double hangtime = 0.0;
    double loadperc = LoadCurrent / 100.0;
    if (loadperc < 0.0) {
      loadperc = 0.0;
    }
    if (loadperc > 1.0) {
      loadperc = 1.0;
    }

    return (LinearPercentIndicator(
      percent: loadperc,
      center: new Text(
        LoadCurrent.toStringAsFixed(2),
        style: new TextStyle(fontWeight: FontWeight.bold, fontSize: 20.0),
      ),
      leading: new Text(
        LoadCurrent.toStringAsFixed(0) + "kg",
        style: new TextStyle(fontWeight: FontWeight.bold, fontSize: 17.0),
      ),
      trailing: new Text(
        hangtime.toStringAsFixed(0) + "s",
        style: new TextStyle(fontWeight: FontWeight.bold, fontSize: 17.0),
      ),
      progressColor: Colors.redAccent,
    )

        //Text("Current load: " + LoadCurrent.toString())
        );
  }

  // ignore: unused_element
  Widget _buildLoadPlot(List<FlSpot> LoadCurrentData) {
    List<Color> gradientColors = [
      // https://api.flutter.dev/flutter/dart-ui/Color-class.html
      const Color.fromRGBO(0, 0, 200, 0.4),
      const Color.fromRGBO(200, 0, 0, 1.0),
    ];
    return Row(children: [
      LoadCurrentData.length < 3
          ? Text("No Hang - No Load")
          : Expanded(
              flex: 3,
              child: AspectRatio(
                aspectRatio: 3,
                child: Container(
                  child: Padding(
                    padding: const EdgeInsets.only(
                        right: 0.0, left: 0.0, top: 0, bottom: 0),
                    child: LineChart(
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
                              return value.toInt().toString();
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
                              return value.toInt().toString();
                            },
                            reservedSize: 28,
                            margin: 12,
                          ),
                        ),
                        borderData: FlBorderData(
                            show: true,
                            border: Border.all(
                                color: const Color(0xff37434d), width: 1)),
                        minY: 0,
                        lineBarsData: [
                          LineChartBarData(
                            spots: LoadCurrentData,
                            colors: gradientColors,
                            barWidth: 5,
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
            )
    ]);
  }

  Widget _buildWorkoutSelector(
      String SelectedWorkout, List<String> WorkoutList) {
    // ignore: unused_local_variable
    String dropdownValue = SelectedWorkout;
    //_sendListWorkouts(); // FIXME
    return (Column(
      children: [
        Text("Select Workout"),
        Text(SelectedWorkout)
        //Text(WorkoutList.toString()),
        // FIXME: does not display the string map?!
        /*
        DropdownButton<String>(
          // items: <String>['HRST-S1', 'Two', 'Free', 'Four'] // FIXME
          items: WorkoutList // FIXME
              .map<DropdownMenuItem<String>>((String value) {
            return DropdownMenuItem<String>(
              value: value,
              child: Text(value),
            );
          }).toList(),
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
        )*/
      ],
    ));
  }

  // ignore: unused_element
  Widget _buildEditableColumn() {
    return Padding(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        children: <Widget>[
          _buildTextFieldWith(_hostTextController, 'Enter broker address',
              currentAppState.getAppConnectionState),
          const SizedBox(height: 10),
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

  // ignore: unused_element
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

  // ignore: unused_element
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
      double TimerDuration,
      double TimerElapsed,
      double TimerCompleted,
      double TimerCountdown,
      int CurrentSet,
      int TotalSets,
      int CurrentRep,
      int TotalReps) {
    Wakelock.enable(); // Stay awake, once data has been received

    if (TimerCountdown == 10.0) {
      _playSFX("images/10.mp3");
    }
    if (TimerCountdown == 9.0) {
      _playSFX("images/9.mp3");
    }
    if (TimerCountdown == 8.0) {
      _playSFX("images/8.mp3");
    }
    if (TimerCountdown == 7.0) {
      _playSFX("images/7.mp3");
    }
    if (TimerCountdown == 6.0) {
      _playSFX("images/6.mp3");
    }
    if (TimerCountdown == 5.0) {
      _playSFX("images/5.mp3");
    }
    if (TimerCountdown == 4.0) {
      _playSFX("images/4.mp3");
    }
    if (TimerCountdown == 3.0) {
      _playSFX("images/3.mp3");
    }
    if (TimerCountdown == 2.0) {
      _playSFX("images/2.mp3");
    }
    if (TimerCountdown == 1.0) {
      _playSFX("images/1.mp3");
    }
    if (TimerCountdown == 0.0) {
      _playSFX("images/done.mp3");
    }

    double PercentSets = TotalSets == 0 ? 0 : CurrentSet / TotalSets;
    double PercentReps = TotalReps == 0 ? 0 : CurrentRep / TotalReps;
    if (PercentSets > 1) {
      PercentSets = 1.0;
    }
    if (PercentReps > 1) {
      PercentReps = 1.0;
    }
    if (TimerCompleted > 1) {
      TimerCompleted = 1.0;
    }
    if (PercentSets < 0) {
      PercentSets = 0.0;
    }
    if (PercentReps < 0) {
      PercentReps = 0.0;
    }
    if (TimerCompleted < 0) {
      TimerCompleted = 0.0;
    }
    return Column(
      children: [
        new LinearPercentIndicator(
          animation: false,
          animationDuration: 100,
          lineHeight: 20.0,
          percent: TimerCompleted,
          center: Text(TimerElapsed.toInt().toString() +
              " / " +
              TimerDuration.toInt().toString() +
              " Seconds"),
          linearStrokeCap: LinearStrokeCap.butt,
          progressColor: Colors.red,
        ),
        new LinearPercentIndicator(
          animation: false,
          animationDuration: 100,
          lineHeight: 20.0,
          percent: PercentReps,
          center: Text(CurrentRep.toStringAsFixed(0) +
              " / " +
              TotalReps.toStringAsFixed(0) +
              " Reps"),
          linearStrokeCap: LinearStrokeCap.butt,
          progressColor: Colors.red,
        ),
        new LinearPercentIndicator(
          animation: false,
          animationDuration: 100,
          lineHeight: 20.0,
          percent: PercentSets,
          center: Text(CurrentSet.toStringAsFixed(0) +
              " / " +
              TotalSets.toStringAsFixed(0) +
              " Sets"),
          linearStrokeCap: LinearStrokeCap.butt,
          progressColor: Colors.red,
        )
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
          child: Icon(Icons.pause)),
      FloatingActionButton(
          onPressed: _sendMessageStop, child: Icon(Icons.stop)),
      FloatingActionButton(
          onPressed: _sendMessageRestart, // FIXME: implement
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
        height: 50,
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
  // ignore: unused_element
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
    String myIdentifier = 'Hangboard App'; // FIXME

    manager = MQTTManager(
        host: "hangboard", //FIXME: make configurable
        topic: "hangboard/workout/timerstatus", //_topicTextController.text,
        identifier: myIdentifier,
        state: currentAppState);
    manager.initializeMQTTClient();
    manager.connect();

// Get inital list of workouts
    _sendListWorkouts();
  }

  void _disconnect() {
    manager.disconnect();
  }

  void _sendListWorkouts() {
    _publishMessage("ListWorkouts");
  }

  void _sendMessageStart() {
    _publishMessage("Start");
  }

  void _sendMessageStop() {
    _publishMessage("Stop");
  }

  void _sendMessageRestart() {
    _publishMessage("Restart");
  }

  void _sendMessagePause() {
    _publishMessage("Pause");
  }

  void _publishMessage(String text) {
    final String message = text;
    manager.publish_topic("hangboard/workout/control", message); // FIXME
    _messageTextController.clear();
  }

  _playSFX(String Filename) async {
    //await Isolate.spawn(assetsAudioPlayer.open, Audio(Filename));

    await assetsAudioPlayer.open(
      Audio(Filename),
    );
  }

  // ignore: unused_element
  _playSFX10() {
    // await assetsAudioPlayer.open(Audio("images/10.mp3"), autoStart: false);
    PlaySFX10.play();
  }

  // ignore: unused_element
  _playSFX9() async {
    await assetsAudioPlayer.open(
      Audio("images/9.mp3"),
    );
  }

  // ignore: unused_element
  _playSFX8() async {
    await audioPlayer.play("images/8.mp3", isLocal: true);
  }

  // ignore: unused_element
  _playSFX7() async {
    await audioPlayer.play("images/7.mp3", isLocal: true);
  }

  // ignore: unused_element
  _playSFX6() async {
    await audioPlayer.play("images/6.mp3", isLocal: true);
  }

  // ignore: unused_element
  _playSFX5() async {
    await audioPlayer.play("images/5.mp3", isLocal: true);
  }

  // ignore: unused_element
  _playSFX4() async {
    await audioPlayer.play("images/4.mp3", isLocal: true);
  }

  // ignore: unused_element
  _playSFX3() async {
    await audioPlayer.play("images/3.mp3", isLocal: true);
  }

  // ignore: unused_element
  _playSFX2() async {
    await audioPlayer.play("images/2.mp3", isLocal: true);
  }

  // ignore: unused_element
  _playSFX1() async {
    await audioPlayer.play("images/1.mp3", isLocal: true);
  }

  /*_playSFXDone() async {
    await audioPlayer.play("images/done.mp3", isLocal: true);
  }*/

}
