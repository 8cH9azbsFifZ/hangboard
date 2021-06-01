# Exercises Dockerfile
FROM python:3.9

WORKDIR /app/
COPY requirements.txt /app/
RUN pip install -r requirements.txt

WORKDIR /app/
COPY . /app

CMD python3 boards.py --host 0.0.0.0 --port 4324

EXPOSE 4324
