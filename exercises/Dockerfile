# Exercises Dockerfile
FROM python:3.9

WORKDIR /app/
COPY requirements.txt /app/
RUN pip install -r requirements.txt

WORKDIR /app/boards
COPY ./boards/* .

WORKDIR /app/exercises
COPY * .

CMD ./startup.sh

EXPOSE 9090 9091
