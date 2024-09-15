import sqlite3
from flask_bcrypt import Bcrypt
from flask import Flask


app = Flask(__name__)
bcrypt = Bcrypt(app)


db_path = 'databases/testgpt.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Fetch all users' plaintext passwords
cursor.execute("SELECT teacher_id, teacher_password FROM teachers")
users = cursor.fetchall()

# Hash each password and update it
for user_id, plain_password in users:
    hashed_password = bcrypt.generate_password_hash(plain_password).decode('utf-8')
    cursor.execute("UPDATE teachers SET teacher_password = ? WHERE teacher_id = ?",
                   (hashed_password, user_id))

# Commit changes and close connection
conn.commit()
conn.close()

print("All passwords have been hashed and updated in the database.")
