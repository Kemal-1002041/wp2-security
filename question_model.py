import sqlite3

class QuestionModel():
    def __init__(self):
        self.db = 'databases/testgpt.db'
        self.conn_db = sqlite3.connect(self.db)

    def get_cursor(self):
        cursor = self.conn_db.cursor()
        cursor.row_factory = sqlite3.Row
        return cursor
    
    def save_question(self, note_id, question):
        cursor = self.get_cursor()
        query = """INSERT INTO questions (note_id, exam_question)
                    VALUES (?, ?)"""
        cursor.execute(query, (note_id, question))
        self.conn_db.commit()

    def change(self, questions_id, question):
        cursor = self.get_cursor()
        query = """UPDATE questions SET exam_question = ? WHERE questions_id = ?"""
        cursor.execute(query, (question, questions_id))
        self.conn_db.commit()

    def delete(self, questions_id):
        cursor = self.get_cursor()
        query = "DELETE FROM questions WHERE questions_id = ?"
        cursor.execute(query, (questions_id,))
        self.conn_db.commit()

    def get_question_from_noteID(self, note_id):
        cursor = self.get_cursor()
        query = """SELECT questions_id, exam_question FROM questions
                    WHERE note_id = ?"""
        cursor.execute(query, (note_id,))
        return cursor.fetchall()
    
    def get_question(self, questions_id):
        cursor = self.get_cursor()
        query = """SELECT note_id, exam_question FROM questions
                    WHERE questions_id = ?"""
        cursor.execute(query, (questions_id,))
        return cursor.fetchone()