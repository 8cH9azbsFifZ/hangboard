from database import Database


if __name__ == "__main__":
  d = Database()
  d._set_user(uuid="us3r")
  d._record_data(hostname="t20")