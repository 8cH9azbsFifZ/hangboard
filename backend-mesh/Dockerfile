# Exercises Dockerfile
FROM python:3.9

WORKDIR /app/
COPY requirements.txt /app/
RUN pip install -r requirements.txt

WORKDIR /app/
COPY * .

CMD python3 mesh.py --socket_exercise ws://127.0.0.1:4321  --socket_gyroscope ws://127.0.0.1:4324 