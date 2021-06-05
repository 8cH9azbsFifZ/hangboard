Linking the microservices in the backend and implement the integrating logic. These parts
shall not be implemented in the frontend processes.

# Starting
On OSX: 
```
python3 -m venv venv
source venv/bin/activate
python3 mesh.py --socket_exercise ws://127.0.0.1:4321 --socket_gyroscope ws://10.101.40.81:4323
```

## Preparation
```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```