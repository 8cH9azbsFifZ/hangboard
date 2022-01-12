api-doc:
	docker run --rm -it -v $(PWD)/database_api.yaml:/app/asyncapi.yml -v $(PWD)/api:/app/output asyncapi/generator  -o /app/output /app/asyncapi.yml @asyncapi/html-template --force-write

install:
	service="hangboard_record.service"
	echo "Install hangboard service for: hangboard_record.service" 
	sudo cp ./hangboard_record.service /lib/systemd/system/
	sudo chmod 644 /lib/systemd/system/hangboard_record.service
	sudo systemctl daemon-reload
	sudo systemctl enable hangboard_record.service
	sudo systemctl restart hangboard_record.service
