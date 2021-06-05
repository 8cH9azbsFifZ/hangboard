# Exercises Dockerfile
FROM python:3.9

WORKDIR /app/
COPY requirements.txt /app/
RUN pip install -r requirements.txt

WORKDIR /app/boards
COPY ./boards/* .

WORKDIR /app/
ADD workouts /app/workouts
COPY * .

CMD python3 exercises.py --host 0.0.0.0 --port 4321 

EXPOSE 4321
