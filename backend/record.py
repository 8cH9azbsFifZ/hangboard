"""
This service runs the database recorder (listen to MQTT and record to MongoDB)
"""
from database import Database


if __name__ == "__main__":
  d = Database(hostname="hangboard", user="root", password="rootpassword")
  d._set_user(uuid="us3r")
  d._record_data(hostname="hangboard")