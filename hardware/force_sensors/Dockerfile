# Hangboard Web
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

ADD . /app/

CMD python3 force.py --host 0.0.0.0 

EXPOSE 4322
