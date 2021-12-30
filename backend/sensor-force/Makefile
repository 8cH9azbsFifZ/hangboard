api-doc:
	docker run --rm -it -v $(PWD)/sensor_force_api.yaml:/app/asyncapi.yml -v $(PWD)/api:/app/output asyncapi/generator  -o /app/output /app/asyncapi.yml @asyncapi/html-template 
