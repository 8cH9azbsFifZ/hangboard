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
  int _timer_currentset = 0;
  int _timer_totalsets = 0;
  int _timer_currentrep = 0;
  int _timer_totalreps = 0;

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
  bool _intensity_too_high = false;
  bool _intensity_too_high2 =
      false; // internal variable, beacause sound must be played back only once if overload occurs ;)
  bool _intensity_too_high_warn =
      false; // this is the indicator if intensity level is crossed for playback of the sound

// Data on upcoming sets
  String _upcomingsets = "";
  double _remainingtimeinworkout = 0.0;

// Current Set data
  double _current_set_intensity = 0.0;

  void setSetInfo(String text) {
    Map<String, dynamic> jsondata = jsonDecode(text);

    if (jsondata.containsKey("intensity")) {
      _current_set_intensity = jsondata["intensity"];
    }

    notifyListeners();
  }

  void setUpcoming(String text) {
    Map<String, dynamic> jsondata = jsonDecode(text);
    if (jsondata.containsKey("UpcomingSets")) {
      _upcomingsets = jsondata["UpcomingSets"];
    }
    if (jsondata.containsKey("RemainingTime")) {
      _remainingtimeinworkout = (jsondata["RemainingTime"]).toDouble();
    }
    notifyListeners();
  }

  void SetUserStatistics(String text) {
    Map<String, dynamic> userjson = jsonDecode(text);
    if (userjson.containsKey("CurrentIntensity")) {
      _currentintensity = userjson["CurrentIntensity"];
    }

    // WORKAROUND for sound playing mutiple times
    if (_current_set_intensity > 0.0) {
      _intensity_too_high2 = _intensity_too_high;
      if (_current_set_intensity < _currentintensity) {
        _intensity_too_high = true;
      } else {
        _intensity_too_high = false;
      }
      // Set warning only if crossover occurs
      _intensity_too_high_warn = false;
      if (_intensity_too_high2 == false) {
        if (_intensity_too_high == true) {
          _intensity_too_high_warn = true;
        }
      }
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

    if (loadjson.containsKey("HangDetected")) {
      _hangdetected = loadjson["HangDetected"]; //.toLowerCase() == 'true';
    }
    if (loadjson.containsKey("HangChangeDetected")) {
      _hangchangedetected =
          loadjson["HangChangeDetected"]; //.toLowerCase() == 'true';
    }

    if (_hangdetected.contains("False")) {
      _plot_t0 = _plot_time_current;
    }
    if (_hangchangedetected.contains("Hang")) {
      _plot_load_current = [];
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
    if ((_hold_left != "") || (_hold_right != "")) {
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
    if (timerjson.containsKey("CurrentSet")) {
      _timer_currentset = timerjson["CurrentSet"];
    }
    if (timerjson.containsKey("TotalSets")) {
      _timer_totalsets = timerjson["TotalSets"];
    }
    if (timerjson.containsKey("CurrentRep")) {
      _timer_currentrep = timerjson["CurrentRep"];
    }
    if (timerjson.containsKey("TotalReps")) {
      _timer_totalreps = timerjson["TotalReps"];
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
        -1; // WORKAROUND: app will rebuild on every update and start to start sound every microsecond :/ #56
    return a;
  }

  int get getTimerCurrentSet => _timer_currentset;
  int get getTimerTotalSets => _timer_totalsets;
  int get getTimerCurrentRep => _timer_currentrep;
  int get getTimerTotalReps => _timer_totalreps;

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

  double get getCurrentItensity => _currentintensity; // FIXME: typo
  bool get getCurrentIntensityTooHigh => _intensity_too_high_warn;

  String get getUpcomingSets => _upcomingsets;
  double get getRemainingTimeInWorkout => _remainingtimeinworkout;

  double get getCurrentSetIntensity => _current_set_intensity;

  MQTTAppConnectionState get getAppConnectionState => _appConnectionState;
}
