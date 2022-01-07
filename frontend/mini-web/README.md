# Configure websockets in mosquitto:
```
cat 
cat << eof > /etc/mosquitto/conf.d/default.conf
port 1883
listener 9001
protocol websockets
eof
```