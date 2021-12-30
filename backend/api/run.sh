#!/bin/bash
docker run --rm -it \
-v $PWD/asyncapi.yaml:/app/asyncapi.yml \
-v $PWD/out:/app/output \
asyncapi/generator  -o /app/output /app/asyncapi.yml @asyncapi/html-template 
