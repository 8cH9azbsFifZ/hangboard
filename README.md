# Hangboard 

*STATUS: In Development - Towards a working demonstrator*

A universal force and velocity sensing hangboard mount with exercise timers for all hangboards. 
Please have a look at the 
[manual](./doc/Manual.pdf).


# Developing
+ Running the Demonstrator Backend (including web interface)? -> Please look for the README.md instructions in the demonstrator releases.
+ Debugging the websockets `wscat -c "ws://localhost:4323/"`
+ Install flutter and configure correct paths
+ Prepare the virtual python environment
  ```
    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install -r requirements.txt
  ```

For manual startup:
+ Start backend service ```cd backend; python3 ./run_ws.py ```
+ Start the iOS / Android / Web App: `cd flutter_hangboard && flutter run`




