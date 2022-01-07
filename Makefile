backend-doc: # output in ~/backend/doxygen/html
	git checkout gh-pages --quiet
	git checkout dev -- .gitignore
	git checkout dev -- doc
	git checkout dev -- backend

	echo "Build backend documentation"
	rm -rf backend-doc
	rm -rf backend/doxygen
	cd backend ; doxygen ;cd ..
	mv backend/doxygen/html backend-doc

	git add -A
	git commit -a -m  "updated $(date +"%d.%m.%Y %H:%M:%S")"
	git push --quiet

	git checkout dev --quiet


manual-doc:
	git checkout gh-pages --quiet
	git checkout dev -- .gitignore
	git checkout dev -- doc
	git checkout dev -- backend

	echo "Build manual"
	asciidoctor -d book -D ./doc --backend=html5 -o ./index.html doc/Manual.adoc

	git add -A
	git commit -a -m  "updated $(date +"%d.%m.%Y %H:%M:%S")"
	git push --quiet

	git checkout dev --quiet


frontend:
	cd frontend/flutter_hangboard ; 	~/src/flutter/bin/flutter build ios ; 	~/src/flutter/bin/flutter install ; cd ..


movie-sources:
	gource -1280x720  -c 4 --title "Hangboard" -o - . |ffmpeg -i - -preset slow -codec:a libfdk_aac -b:a 128k -codec:v libx264 -pix_fmt yuv420p -b:v 2500k -minrate 1500k -maxrate 4000k -bufsize 5000k -vf scale=-1:720 output.mp4

loc:
	wc -l $((find . -name "*.py" ; find flutter_hangboard/lib/ -name "*.dart" ) |grep -v venv)
