FROM python:3.8
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY board_data board_data
COPY . . 
RUN python3 ./board.py
EXPOSE 5001
CMD [ "flask", "run" , "--port=5001"]

