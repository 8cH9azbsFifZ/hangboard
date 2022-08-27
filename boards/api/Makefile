run:
	flask run

api-doc:
	docker run -it --rm -v $(PWD):/data ghcr.io/redocly/redoc/cli:v2.0.0-rc.59  bundle ./boards_api.yaml
	mv redoc-static.html api/index.html
	
requirements:
	pip3 install -r requirements.txt
