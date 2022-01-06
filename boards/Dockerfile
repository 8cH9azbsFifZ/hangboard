FROM python:3.8
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY board_data board_data
COPY . . 
RUN python3 ./board.py
EXPOSE 5001
CMD [ "flask", "run" , "--host=0.0.0.0", "--port=5001"]

