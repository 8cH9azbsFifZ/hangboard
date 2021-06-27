api-doc: #output in ~/api
	echo "npm install -g @asyncapi/generator"
	rm -rf ../api/
	ag asyncapi.yaml @asyncapi/html-template -o ../api/

backend-doc: # output in ~/backend/doxygen/html
	doxygen 

clean:
	rm -rf ../api/
	rm -rf doxygen