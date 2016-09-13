import sqlite3

con = sqlite3.connect('../images.db')
cursor = con.cursor()

# cursor.execute("CREATE TABLE image(index int, GPS text, Keypoint , Descriptor ")