

api-doc: #output in ~/api
	
	echo "npm install -g @asyncapi/generator"
	cd backend ; rm -rf ../api/ ; ag asyncapi.yaml @asyncapi/html-template -o ../api/ ; cd ..

backend-doc: # output in ~/backend/doxygen/html
	cd backend ; doxygen ;cd ..

frontend:
	cd flutter_hangboard ; 	~/src/flutter/bin/flutter build ios ; 	~/src/flutter/bin/flutter install ; cd ..



clean:
	rm -rf api/
	rm -rf backend/doxygen