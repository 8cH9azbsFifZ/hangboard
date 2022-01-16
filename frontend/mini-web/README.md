# Configure websockets in mosquitto:
```
cat << eof > /etc/mosquitto/conf.d/default.conf
port 1883
listener 9001
protocol websockets
eof
```
+ Restart it `sudo /etc/init.d/mosquitto restart`