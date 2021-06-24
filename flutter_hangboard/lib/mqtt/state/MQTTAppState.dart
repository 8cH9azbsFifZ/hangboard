import 'dart:convert';
// ignore: unused_import
import 'dart:ffi';
import 'package:fl_chart/fl_chart.dart';

import 'package:flutter/cupertino.dart';

enum MQTTAppConnectionState { connected, disconnected, connecting }

class MQTTAppState with ChangeNotifier {
  MQTTAppConnectionState _appConnectionState =
      MQTTAppConnectionState.disconnected;
  String _receivedText = '';
  String _historyText = '';

  double _timer_duration = 0.0;
  double _timer_elapsed = 0.0;
  double _timer_completed = 0.0;
  double _timer_countdown = -1.0;

  String _hold_right = '';
  String _hold_left = '';
  String _imagename_noholds =
      'images/zlagboard_evo.png'; // FIXME: correct image
  String _imagename = 'images/zlagboard_evo.png';

  bool _hangdetected = false;
  bool _hangchangedetected = false;

  String _exercise_type = '';

  List<FlSpot> _plot_load_current = [];

  void setLoadStatus(String text) {
    Map<String, dynamic> loadjson = jsonDecode(text);
    double time = 0.0;
    double load = 0.0;

    if (loadjson.containsKey("time")) {
      time = loadjson["time"];
    }

    if (loadjson.containsKey("loadcurrent")) {
      load = loadjson["loadcurrent"];
    }

    if (loadjson.containsKey("HangDetected")) {
      _hangdetected = loadjson["HangDetected"];
    }
    if (loadjson.containsKey("HangChangeDetected")) {
      _hangchangedetected = loadjson["HangChangeDetected"];
    }

    if (_hangchangedetected == true) {
      if (_hangdetected == true) {
        _plot_load_current = [];
      }
    }

    _plot_load_current.add(FlSpot(time, load));
    //double t0 =
    /*
    if (mytimes.length > 2) {
      double t0 = double.parse(mytimes[0].toString());
      for (int i = 0; i < mytimes.length; i++) {
        mydata.add(FlSpot(
          double.parse(mytimes[i].toString()) - t0,
          double.parse(myload[i].toString()),
        ));
      }
    }*/
  }

  void setReceivedText(String text) {
    _historyText = _receivedText;
    _receivedText = text;
    notifyListeners();
  }

  void setCurrentHolds(String text) {
    Map<String, dynamic> holdsjson = jsonDecode(text);
    if (holdsjson.containsKey("Left")) {
      _hold_left = holdsjson["Left"];
    }

    if (holdsjson.containsKey("Right")) {
      _hold_right = holdsjson["Right"];
    }
    if (_hold_left != "") {
      _imagename =
          'images/zlagboard_evo.' + _hold_left + '.' + _hold_right + '.png';
    } else {
      _imagename = _imagename_noholds;
    }
    notifyListeners();
  }

  void setCurrentTimer(String text) {
    Map<String, dynamic> timerjson = jsonDecode(text);
    if (timerjson.containsKey("Duration")) {
      _timer_duration = timerjson["Duration"];
    }
    if (timerjson.containsKey("Elapsed")) {
      _timer_elapsed = timerjson["Elapsed"];
    }
    if (timerjson.containsKey("Completed")) {
      _timer_completed = timerjson["Completed"];
    }
    if (timerjson.containsKey("Countdown")) {
      _timer_countdown = timerjson["Countdown"];
    }
    notifyListeners();
  }

  void setExerciseType(String text) {
    // Map<String, dynamic> exercisejson = jsonDecode(text);
    //if (timerjson.containsKey("Duration")) {
    //  _timer_duration = timerjson["Duration"];
    //}
    _exercise_type = text;
    notifyListeners();
  }

  void setAppConnectionState(MQTTAppConnectionState state) {
    _appConnectionState = state;
    notifyListeners();
  }

  String get getReceivedText => _receivedText;
  String get getHistoryText => _historyText;
  double get getTimerDuration => _timer_duration;
  double get getTimerElapsed => _timer_elapsed;
  double get getTimerCompleted => _timer_completed;
  double get getTimerCountdown => _timer_countdown;
  String get getHoldLeft => _hold_left;
  String get getHoldRight => _hold_right;
  String get getImageName => _imagename;
  String get getExerciseType => _exercise_type;
  List<FlSpot> get getLoadCurrentData => _plot_load_current;

  MQTTAppConnectionState get getAppConnectionState => _appConnectionState;
}
