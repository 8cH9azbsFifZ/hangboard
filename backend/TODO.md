# Workouts
+ Add capability to select exercise - OPEN: receive the selected exercise

# Exercises
+ Workout type (strength, endurance, ...)
+ Grip type: Grip Half Full Open 
+ Implement Assessment
+ Google Sheet Exercise Input
+ Validator for JSON files!!
+ Create modular building blocks for workouts
+ Basic training plan calculations
+ Calculate increases in workouts
+ Upload Exercises
+ Implement more exercises
+ Exercise 2 JSON
+ Add exercise finger numbers or which fingers
+ Make conjunction with hang detection configurable
+ Generate an exercise preview (with images)

# Boards
+ Add Zlagboard Mini Layout
+ Check other boards (create images etc.)
+ Implement JSON commands

# Backend
+ MongoDB https://realpython.com/introduction-to-mongodb-and-python/
+ Maybe: protobuf to save bandwidth and be safe on types
+ Alternatively: apt-get install mosquitto
+ Interface: documentation and validation https://python-jsonschema.readthedocs.io/en/latest/validate/#the-basics
 https://www.asyncapi.com/github-actions
+ Automatic detection of mqtt master server?
cat sensor_force.py| awk '/ttopic =/{gsub(".*= \"","");gsub("\".*","");base=$0}/_sendmessage/{gsub(".*age\\\(\"","");gsub("\",","");gsub(")","");print base$0}'

npm install -g @asyncapi/generator


npm install -g @asyncapi/generator
ag asyncapi.yaml @asyncapi/html-template -o ./docs
