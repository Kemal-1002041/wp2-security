import sqlite3

class LoginModel():
    def __init__(self):
        self.db = 'databases/testgpt.db'
        self.conn_db = sqlite3.connect(self.db)

    def get_cursor(self):
        cursor = self.conn_db.cursor()
        cursor.row_factory = sqlite3.Row
        return cursor
    
    def get_user(self, username, password):
        cursor = self.get_cursor()
        query = "SELECT * FROM teachers WHERE username = ? AND teacher_password = ?"
        cursor.execute(query, (username, password))
        return cursor.fetchone()

    def get_user_by_username(self, username):
        cursor = self.get_cursor()
        query = "SELECT teacher_id, teacher_password, is_admin FROM teachers WHERE username = ?"
        cursor.execute(query, (username,))
        return cursor.fetchone()