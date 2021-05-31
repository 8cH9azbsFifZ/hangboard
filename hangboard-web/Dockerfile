# Hangboard Web
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

ADD . /app/
ADD ./static /app/static
ADD ./templates /app/templates


CMD python3 main.py --host 0.0.0.0 --port 8080

EXPOSE 8080
