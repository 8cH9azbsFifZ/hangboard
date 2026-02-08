# CLAUDE.md — AI Assistant Guide for Hangboard

## Project Overview

Hangboard is an open-source, universal force and velocity sensing hangboard mount with exercise timers. It enables smart training for rock climbers with real-time force measurements, customizable workouts, and multiple frontend interfaces. The system runs on a Raspberry Pi with load cells (HX711 ADC), communicating via MQTT (Mosquitto broker) to various frontends.

**License:** GPLv3
**Status:** In development (v0.65) — working prototype, not production-ready

## Architecture

The system follows a **microservices pattern** with MQTT pub/sub messaging:

```
[Load Cells / HX711] → [sensor-force service] → MQTT broker ← [workout service]
                                                      ↓
                                    [Flutter app / Web / LED displays]
```

### Backend (Python 3, Raspberry Pi)
- `backend/sensor-force/` — Force measurement service (HX711 driver, publishes to MQTT)
- `backend/workout/` — Workout timer state machine (exercise sequencing, MQTT control)
- `backend/sensor-gyroscope/` — MPU6050 gyroscope with Kalman filtering
- `backend/sensor-distance/` — Distance sensor module
- `backend/database/` — Data persistence (MongoDB, CSV logging)
- `backend/assets-delivery/` — Flask REST API for board images and sounds

### Frontend
- `frontend/flutter_hangboard/` — **Primary UI** (Flutter/Dart, iOS/Android/Web)
- `frontend/display_7segment/` — 7-segment display interface
- `frontend/display_hd44780/` — HD44780 LCD display
- `frontend/display_moonboard/` — Moonboard LED progress bar
- `frontend/mini-web/` — Minimal web frontend

### Data & Configuration
- `boards/` — Hangboard definitions (23 boards as JSON), SVG/PNG generation
- `exercises/` — Workout definitions, exercise protocols, grip type definitions
- `evaluations/` — Data analysis, MVC estimation, plotting tools

## Key Entry Points

| Component | Entry Point | Purpose |
|-----------|------------|---------|
| Force sensor | `backend/sensor-force/sensor_force.py` | Main sensor daemon |
| Workout timer | `backend/workout/workout.py` | Exercise state machine |
| Assets API | `backend/assets-delivery/app.py` | Flask REST server |
| Flutter app | `frontend/flutter_hangboard/lib/main.dart` | Mobile/web UI |

## Development Setup

### Python Backend
```bash
pip install -r backend/requirements.txt
# For sensor emulation (no hardware): emulated_hx711.py is available
```

### Flutter Frontend
```bash
cd frontend/flutter_hangboard
flutter pub get
flutter run
```

### Board Image Generation
```bash
cd boards
# Uses Docker for image generation
make
```

## Running Tests

```bash
# Backend workout counter tests
python backend/workout/test_counter.py

# Flutter tests
cd frontend/flutter_hangboard && flutter test
```

There is no CI/CD pipeline or formal test framework configured. Tests are run manually.

## MQTT Topic Conventions

All topics use the `hangboard/` prefix with hierarchical paths:

- `hangboard/sensor/load/loadstatus` — Real-time force data
- `hangboard/sensor/lastexercise` — Completed exercise summary
- `hangboard/workout/control` — Workout start/stop/pause
- `hangboard/workout/timerstatus` — Timer state updates
- `hangboard/workout/setinfo` — Current set information

API specs are documented in AsyncAPI 2.0.0 format:
- `backend/sensor-force/sensor_force_api.yaml`
- `backend/workout/workout_api.yaml`

## Code Conventions

### Python
- **Classes:** PascalCase (`HX711`, `Counter`, `Workout`)
- **Functions/variables:** snake_case (`set_reference_unit()`, `get_hold_for_type()`)
- **Logging:** Use `logging` module with thread names:
  ```python
  logging.basicConfig(level=logging.DEBUG, format='ServiceName(%(threadName)-10s) %(message)s')
  ```
- **MQTT setup:** Each service independently creates and connects its own `paho.mqtt.client.Client()`
- **Config:** Hardware config in INI files (`hangboard.ini`), data in JSON
- **Cross-module imports:** Use `sys.path.append('../../boards')` for shared modules

### Flutter/Dart
- **State management:** Provider pattern (`ChangeNotifier`)
- **File naming:** camelCase (`mqttView.dart`, `MQTTManager.dart`)
- **Structure:** `lib/widgets/` for UI, `lib/mqtt/` for MQTT client and state

### Data Formats
- **Workout JSON structure:** Array of `Sets`, each with `Rest-to-Start`, `Exercise`, `Counter`, `Pause`, `Reps`, `Left`, `Right`, `Type`, optional `Intensity`
- **Board JSON:** Hold definitions with positions, types, and depths
- **Grip types:** Defined in `exercises/finger.json`

## Important Patterns

- **Emulation mode:** Backend services have emulated drivers (`emulated_hx711.py`, `emulated_gyroscope.py`) for development without hardware
- **Systemd services:** Production deployment uses systemd (`hangboard_sensor_force.service`, `hangboard_workout.service`)
- **Makefiles:** Each backend module has a Makefile with install and API doc generation targets
- **Board images:** SVGs generated from JSON configs, converted to PNG for Flutter (cached in `boards/cache/`)

## What NOT to Do

- Do not remove or modify emulated driver files — they are essential for non-hardware development
- Do not change MQTT topic paths without updating both backend publishers and frontend subscribers
- Do not modify board JSON schemas without checking `boards/board.py` and `boards/svg_board.py`
- Do not add Python linting configs or formatters — the project does not currently enforce them
- Do not restructure the `sys.path.append` import pattern without a project-wide migration plan

## Project-Specific Domain Knowledge

- **MVC:** Maximum Voluntary Contraction (peak force measurement)
- **FTI:** Force-Time Integral (area under force curve)
- **RFD:** Rate of Force Development
- **Critical Force:** Endurance threshold metric
- **Protocols:** Eva Lopez MaxHangs/IntHangs/SubHangs, Eric Horst 7-53 — these are established climbing training protocols
- **Hold types:** Crimp, half-crimp, open hand, pocket (2/3/4 finger), sloper, pinch, jug
