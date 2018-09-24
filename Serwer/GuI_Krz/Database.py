import sqlite3

with sqlite3.connect("Users.db") as db:
    cursor = db.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
userID INTEGER PRIMARY KEY,
username VARCHAR(20) NOT NULL,
PIN VARCHAR(20) NOT NULL,
password VARCHAR(20) NOT NULL);
''')


# cursor.execute('''
# INSERT INTO user (username, PIN, password)
# VALUES("bob", "1111", "bob")
# ''')

db.commit()

cursor.execute("SELECT * FROM user")

print (cursor.fetchall())
