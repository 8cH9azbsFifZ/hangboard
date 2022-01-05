FROM python:3.8
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY boards boards
WORKDIR /app/backend

CMD [ "python", "./run_ws.py" ]

