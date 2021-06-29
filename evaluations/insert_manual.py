from ../backend/database import Database


if __name__ == "__main__":
    d = Database(hostname="hangboard", user="root", password="rootpassword")
    d._set_user(uuid="us3r")
    #Insert some test data
    d._set_user_maxload(1624911758.3495529, "20mm", 65.2, 10, "both")
    d._set_user_maxload(1624911758.3495529, "JUG", 79.72, 10, "both")
    d._set_user_maxload(1624911799.3495529, "JUG", 94.47, 10, "both")
    d._set_user_maxload(1624911758.3495529, "20mm", 47.89, 10, "left")
    d._set_user_maxload(1624911758.3495529, "20mm", 49.95, 10, "right")
    d._set_user_maxload(1624911758.3495529, "30mm", 94.47, 10, "both")
    d._set_user_bodyweight(1624911758.3495529, 79.72)

