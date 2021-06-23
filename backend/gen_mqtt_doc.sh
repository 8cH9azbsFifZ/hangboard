#!/bin/bash
cat sensor_force.py| awk '/ttopic =/{gsub(".*= \"","");gsub("\".*","");base=$0}/_sendmessage/{gsub(".*age\\\(\"","");gsub("\",","");gsub(")","");print base$0}'|grep -v None
cat workout.py| awk '/ttopic =/{gsub(".*= \"","");gsub("\".*","");base=$0}/_sendmessage/{gsub(".*age\\\(\"","");gsub("\",","");gsub(")","");print base$0}'| grep -v None

cat << eof
mosquitto_pub -h localhost -t hangboard/workout/control -m Start
mosquitto_sub -h localhost -t hangboard/workout/timerstatus
eof
