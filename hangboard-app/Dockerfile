# Hangboard Web
FROM python:3.9

WORKDIR app
COPY * /app/
RUN pip install -r requirements.txt
CMD python3 main.py

EXPOSE 5000 9090 9091
