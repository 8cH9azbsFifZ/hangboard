api-doc:
	docker run --rm -it -v $(PWD)/sensor_force_api.yaml:/app/asyncapi.yml -v $(PWD)/api:/app/output asyncapi/generator  -o /app/output /app/asyncapi.yml @asyncapi/html-template --force-write

install:
	service="hangboard_sensor_force.service"
	echo "Install hangboard service for: hangboard_sensor_force.service" 
	sudo cp ./hangboard_sensor_force.service /lib/systemd/system/
	sudo chmod 644 /lib/systemd/system/hangboard_sensor_force.service
	sudo systemctl daemon-reload
	sudo systemctl enable hangboard_sensor_force.service
	sudo systemctl restart hangboard_sensor_force.service

stop:
	sudo systemctl stop hangboard_sensor_force.service