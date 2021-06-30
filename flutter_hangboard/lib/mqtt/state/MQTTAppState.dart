import 'dart:convert';
// ignore: unused_import
//import 'dart:ffi'; // FIXME
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/cupertino.dart';

enum MQTTAppConnectionState { connected, disconnected, connecting }

class MQTTAppState with ChangeNotifier {
  MQTTAppConnectionState _appConnectionState =
      MQTTAppConnectionState.disconnected;

  // Outdated debugging stuff
  String _receivedText = '';
  String _historyText = '';

// Timer variables
  double _timer_duration = 0.0;
  double _timer_elapsed = 0.0;
  double _timer_completed = 0.0;
  double _timer_countdown = -1.0;

// Variables for board and hold configuration
  String _hold_right = '';
  String _hold_left = '';
  String _imagename_noholds =
      'images/zlagboard_evo.png'; // FIXME: correct image
  String _imagename = 'images/zlagboard_evo.png';

// Hang status and co
  String _hangdetected = '';
  String _hangchangedetected = '';

// Workout variables
  String _workout_selected_id = '';
  String _workout_selected_name = '';
  List<String> _workout_ids = [];
  List<String> _workout_names = [];
  // ignore: unused_field
  int _workout_selected_index = 0;
  // ignore: todo
  // TODO List of workouts

// Exercise variables
  String _exercise_type = '';

// Variables for plot generation
  List<FlSpot> _plot_load_current = [];
  double _load_current = 0.0;
  double _plot_t0 = 0.0;
  double _plot_time_current = 0.0;

  // Variables for summary of last exercise
  double _lasthangtime = 0.0;
  double _lastpausetime = 0.0;
  double _lastmaximalload = 0.0;

  // User statistics
  double _currentintensity = 0.0;

  void SetUserStatistics(String text) {
    Map<String, dynamic> userjson = jsonDecode(text);
    if (userjson.containsKey("CurrentIntensity")) {
      _currentintensity = userjson["CurrentIntensity"];
    }
    notifyListeners();
  }

  void setWorkoutStatus(String text) {
    Map<String, dynamic> workoutjson = jsonDecode(text);

    if (workoutjson.containsKey("ID")) {
      _workout_selected_id = workoutjson["ID"];
    }

    if (workoutjson.containsKey("Name")) {
      _workout_selected_name = workoutjson["Name"];
    }

    notifyListeners();
  }

  void setLastExercise(String text) {
    Map<String, dynamic> exercisejson = jsonDecode(text);
    if (exercisejson.containsKey("LastHangTime")) {
      _lasthangtime = exercisejson["LastHangTime"];
    }
    if (exercisejson.containsKey("LastPauseTime")) {
      _lastpausetime = exercisejson["LastPauseTime"];
    }
    if (exercisejson.containsKey("MaximalLoad")) {
      _lastmaximalload = exercisejson["MaximalLoad"];
    }
    notifyListeners();
  }

  void SetWorkoutList(String text) {
    print("Set Workout list");
    Map<String, dynamic> workoutjson = jsonDecode(text);
    _workout_ids = [];
    _workout_names = [];

    for (int i = 0; i < workoutjson["WorkoutList"].length; i++) {
      _workout_ids.add((workoutjson["WorkoutList"][i]["ID"]).toString());
      _workout_names.add((workoutjson["WorkoutList"][i]["Name"]).toString());
    }

    notifyListeners();
  }

  void setSensorStatus(String text) {
    Map<String, dynamic> sensorjson = jsonDecode(text);

    if (sensorjson.containsKey("HangDetected")) {
      _hangdetected = sensorjson["HangDetected"]; //.toLowerCase() == 'true';
    }
    if (sensorjson.containsKey("HangChangeDetected")) {
      _hangchangedetected =
          sensorjson["HangChangeDetected"]; //.toLowerCase() == 'true';
    }

    if (_hangdetected.contains("False")) {
      _plot_t0 = _plot_time_current;
    }
    if (_hangchangedetected.contains("Hang")) {
      _plot_load_current = [];
    }
    notifyListeners();
  }

  void setLoadStatus(String text) async {
    Map<String, dynamic> loadjson = jsonDecode(text);
    double time = 0.0;
    double load = 0.0;

    if (loadjson.containsKey("time")) {
      time = await loadjson["time"];
    }

    if (loadjson.containsKey("loadcurrent")) {
      load = await loadjson["loadcurrent"];
    }

    _plot_time_current = time;
    time = time - _plot_t0;

    if (_hangdetected.contains("True")) {
      _plot_load_current.add(FlSpot(time, load));
      _load_current = load;
    }

    notifyListeners();
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
  double get getTimerCountdown {
    double a = _timer_countdown;
    _timer_countdown =
        -1; // FIX: app will rebuild on every update and start to start sound every microsecond :/ #56
    return a;
  }

  //=> _timer_countdown;
  String get getHoldLeft => _hold_left;
  String get getHoldRight => _hold_right;
  String get getImageName => _imagename;
  String get getExerciseType => _exercise_type;
  List<FlSpot> get getLoadCurrentData => _plot_load_current;

  String get getWorkoutID => _workout_selected_id;
  String get getWorkoutName => _workout_selected_name;
  List<String> get GetWorkoutList => _workout_ids;
  double get getLoadCurrent => _load_current;

  double get getLastHangTime => _lasthangtime;
  double get getLastPauseTime => _lastpausetime;
  double get getLastMaximalLoad => _lastmaximalload;

  double get getCurrentItensity => _currentintensity;

  MQTTAppConnectionState get getAppConnectionState => _appConnectionState;
}
