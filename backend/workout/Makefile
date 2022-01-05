api-doc:
	docker run --rm -it -v $(PWD)/workout_api.yaml:/app/asyncapi.yml -v $(PWD)/api:/app/output asyncapi/generator  -o /app/output /app/asyncapi.yml @asyncapi/html-template --force-write

install:
	service="hangboard_workout.service"
	echo "Install hangboard service for: hangboard_workout.service" 
	sudo cp ./hangboard_workout.service /lib/systemd/system/
	sudo chmod 644 /lib/systemd/system/hangboard_workout.service
	sudo systemctl daemon-reload
	sudo systemctl enable hangboard_workout.service
	sudo systemctl restart hangboard_workout.service
