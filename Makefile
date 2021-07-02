api-doc: #output in ~/api
	
	branch=main
	git checkout gh-pages --quiet

	#git rm -r * --quiet

	git checkout $branch -- .gitignore
	git checkout $branch -- doc
	git checkout $branch -- backend

	echo "Build API documentation"
	echo "npm install -g @asyncapi/generator"
	rm -rf api
	mkdir api
	cd backend ; ag asyncapi.yaml @asyncapi/html-template -o ../api/ ; cd ..


	git add -A
	git commit -a -m  "updated $(date +"%d.%m.%Y %H:%M:%S")"
	git push --quiet

	git checkout $branch --quiet


backend-doc: # output in ~/backend/doxygen/html
	cd backend ; doxygen ;cd ..

frontend:
	cd flutter_hangboard ; 	~/src/flutter/bin/flutter build ios ; 	~/src/flutter/bin/flutter install ; cd ..

backend:
	docker-compose build

movie-sources:
	gource -1280x720  -c 4 --title "Hangboard" -o - . |ffmpeg -i - -preset slow -codec:a libfdk_aac -b:a 128k -codec:v libx264 -pix_fmt yuv420p -b:v 2500k -minrate 1500k -maxrate 4000k -bufsize 5000k -vf scale=-1:720 output.mp4

loc:
	wc -l $((find . -name "*.py" ; find flutter_hangboard/lib/ -name "*.dart" ) |grep -v venv)

clean:
	rm -rf api/
	rm -rf backend/doxygen
