api-doc:
	docker run --rm -it -v $(PWD)/sensor_force_api.yaml:/app/asyncapi.yml -v $(PWD)/api:/app/output asyncapi/generator  -o /app/output /app/asyncapi.yml @asyncapi/html-template --force-write

install:
	service="hangboard_sensor_force.service"

	echo "Install hangboard service for: "$(service) 

	sudo cp ./$(service) /lib/systemd/system/
	sudo chmod 644 /lib/systemd/system/$(service)
	sudo systemctl daemon-reload
	sudo systemctl enable $(service)
	sudo systemctl restart $(service)
