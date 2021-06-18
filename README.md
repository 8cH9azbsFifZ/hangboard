# Hangboard 

*STATUS: In Development - Towards a working demonstrator*

A universal force and velocity sensing hangboard mount with exercise timers for all hangboards. 
Please have a look at the [manual](https://8ch9azbsfifz.github.io/hangboard/doc/index.html).

# Developing
+ Running the Demonstrator Backend (including web interface)? -> Please look for the README.md instructions in the demonstrator releases.
+ Debugging the websockets `wscat -c "ws://localhost:4323/"`
+ Install flutter and configure correct paths
+ Install dependencies on raspi: `sudo apt-get install libxslt-dev`
+ Prepare the virtual python environment
  ```
    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install -r backend/requirements.txt
  ```

For manual startup:
+ Start backend service ```cd backend; python3 ./run_ws.py ```
+ Start the iOS / Android / Web App: `cd flutter_hangboard && flutter run`


# Creating the documentation
+ Install `brew install asciidoctor`
+ Create the PDF `asciidoctor-pdf Manual.adoc`
+ The documentation in html format is automatically generated using a commit hook on github.
+ Documentation of the backend software can be created using `doxygen` (cf. Doxyfile).
