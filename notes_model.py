import sqlite3
import os
import re


class NotesModel():
    def __init__(self):
        self.db = 'databases/testgpt.db'
        self.conn_db = sqlite3.connect(self.db)

    def get_cursor(self):
        cursor = self.conn_db.cursor()
        cursor.row_factory = sqlite3.Row
        return cursor

    def get_categories(self):
        cursor = self.get_cursor()
        cursor.execute("SELECT category_id, omschrijving FROM categories")
        return cursor.fetchall()

    def get_note(self, note_id):
        cursor = self.get_cursor()
        cursor.execute("SELECT *, teachers.display_name "
                       "FROM notes "
                       "INNER JOIN teachers ON notes.teacher_id = teachers.teacher_id "
                       "WHERE note_id = ?", (note_id,))
        return cursor.fetchone()

    def get_actual_note(self, note_id):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM notes WHERE note_id = ?", (note_id,))
        return cursor.fetchone()

    def get_all_notes(self, teacher_id=None, page_number=1, notes_per_page=10):
        cursor = self.get_cursor()

        offset = (page_number - 1) * notes_per_page

        base_query = """
        SELECT notes.note_id, title, is_public, notes.date_created, categories.omschrijving, teachers.display_name,
            count(questions.exam_question) AS with_questions
        FROM notes
        INNER JOIN categories ON notes.category_id = Categories.category_id
        INNER JOIN teachers ON notes.teacher_id = teachers.teacher_id
        LEFT JOIN questions ON notes.note_id = questions.note_id
        """

        if teacher_id is None:
            query = base_query + " GROUP BY notes.note_id LIMIT ? OFFSET ?"
            cursor.execute(query, (notes_per_page, offset))
        else:
            query = base_query + " WHERE notes.teacher_id = ? GROUP BY notes.note_id LIMIT ? OFFSET ?"
            cursor.execute(query, (teacher_id, notes_per_page, offset))

        return cursor.fetchall()

    def get_all_notes_for_csv(self, teacher_id=None):
        cursor = self.get_cursor()

        base_query = """
        SELECT note_id, title, is_public, notes.note, notes.date_created, categories.omschrijving, teachers.display_name
        FROM notes
        INNER JOIN categories ON notes.category_id = Categories.category_id
        INNER JOIN teachers ON notes.teacher_id = teachers.teacher_id
        """

        if teacher_id is None:
            query = base_query
            cursor.execute(query)
        else:
            query = base_query + " WHERE notes.teacher_id = ? "
            cursor.execute(query)

        return cursor.fetchall()

    def count_all_notes(self, teacher_id=None):
        cursor = self.get_cursor()

        if teacher_id is None:
            query = "SELECT COUNT(*) FROM notes"
            cursor.execute(query)
        else:
            query = "SELECT COUNT(*) FROM notes WHERE teacher_id = ?"
            cursor.execute(query, (teacher_id,))

        count = cursor.fetchone()[0]
        return count

    def get_all_public_notes(self, teacher_id=None, page_number=1, notes_per_page=10):
        cursor = self.get_cursor()
        offset = (page_number - 1) * notes_per_page
        query = """SELECT notes.note_id, title, is_public, notes.date_created,  
                    categories.omschrijving, teachers.display_name,
                    count(questions.exam_question) AS with_questions  
                    FROM notes  
                    INNER JOIN categories  
                    ON notes.category_id = categories.category_id  
                    INNER JOIN teachers ON notes.teacher_id = teachers.teacher_id
                    LEFT JOIN questions ON notes.note_id = questions.note_id
                    WHERE notes.teacher_id = ? OR notes.is_public = 1
                    GROUP BY notes.note_id
                    LIMIT ? OFFSET ?"""
        cursor.execute(query, (teacher_id, notes_per_page, offset))
        return cursor.fetchall()

    def count_all_public_notes(self, teacher_id):
        cursor = self.get_cursor()
        query = """SELECT COUNT(*) FROM notes 
                   WHERE teacher_id = ? OR is_public = 1"""
        cursor.execute(query, (teacher_id,))
        count = cursor.fetchone()[0]
        return count

    def get_filtered_notes(self, category, teacher_id=None, page_number=1, notes_per_page=10):
        cursor = self.get_cursor()
        offset = (page_number - 1) * notes_per_page
        base_query = """
            SELECT notes.note_id, title, is_public, notes.date_created, categories.omschrijving, 
            teachers.display_name,
                count(questions.exam_question) AS with_questions
            FROM notes
            INNER JOIN categories ON notes.category_id = Categories.category_id
            INNER JOIN teachers ON notes.teacher_id = teachers.teacher_id
            LEFT JOIN questions ON notes.note_id = questions.note_id
        """

        if teacher_id is None:
            query = base_query + " WHERE notes.category_id = ? GROUP BY notes.note_id LIMIT ? OFFSET ?"
            cursor.execute(query, (category, notes_per_page, offset))
        else:
            query = base_query + (" WHERE notes.category_id = ? AND notes.teacher_id = ? "
                                  "GROUP BY notes.note_id LIMIT ? OFFSET ?")
            cursor.execute(query, (category, teacher_id, notes_per_page, offset))

        return cursor.fetchall()

    def count_filtered_notes(self, category, teacher_id=None):
        cursor = self.get_cursor()

        if teacher_id is None:
            query = "SELECT COUNT(*) FROM notes WHERE category_id = ?"
            cursor.execute(query, (category,))
        else:
            query = "SELECT COUNT(*) FROM notes WHERE category_id = ? AND teacher_id = ?"
            cursor.execute(query, (category, teacher_id))

        count = cursor.fetchone()[0]
        return count

    def get_searched_notes(self, note, title, teacher_id=None, page_number=1, notes_per_page=10):
        cursor = self.get_cursor()
        offset = (page_number - 1) * notes_per_page

        base_query = """
        SELECT notes.note_id, title, is_public, notes.date_created, categories.omschrijving, 
        teachers.display_name, note,
        count(questions.exam_question) AS with_questions
        FROM notes
        INNER JOIN categories ON notes.category_id = Categories.category_id
        INNER JOIN teachers ON notes.teacher_id = teachers.teacher_id
        LEFT JOIN questions ON notes.note_id = questions.note_id
        WHERE (note LIKE ? OR title LIKE ?)
        """

        search_parameters = ['%' + note + '%', '%' + title + '%']

        if teacher_id is None:
            query = base_query + " GROUP BY notes.note_id LIMIT ? OFFSET ?"
            search_parameters.extend([notes_per_page, offset])
        else:
            query = base_query + " AND notes.teacher_id = ? GROUP BY notes.note_id LIMIT ? OFFSET ?"
            search_parameters.extend([teacher_id, notes_per_page, offset])

        cursor.execute(query, search_parameters)
        return cursor.fetchall()

    def count_searched_notes(self, note, title, teacher_id=None):
        cursor = self.get_cursor()
        search_parameters = ['%' + note + '%', '%' + title + '%']

        base_query = """
        SELECT COUNT(*)
        FROM notes
        INNER JOIN categories ON notes.category_id = Categories.category_id
        INNER JOIN teachers ON notes.teacher_id = teachers.teacher_id
        WHERE (note LIKE ? OR title LIKE ?)
        """

        if teacher_id is None:
            query = base_query
        else:
            query = base_query + " AND notes.teacher_id = ? "
            search_parameters.append(teacher_id)

        cursor.execute(query, search_parameters)
        count = cursor.fetchone()[0]
        return count

    def save_dict(self, dict):
        cursor = self.get_cursor()
        cursor.execute("INSERT INTO notes (title, note_source, is_public, teacher_id, category_id, note) "
                       "VALUES (?, ?, ?, ?, ?, ?)",
                       (dict['key_title'], dict['key_note_source'],
                        dict['key_is_public'], dict['key_teacher_id'], dict['key_category_id'], dict['key_note']))
        self.conn_db.commit()

    def change_note(self, note_id, dict):
        cursor = self.get_cursor()
        cursor.execute("UPDATE notes SET title = ?, note_source = ?, is_public = ?, "
                       "teacher_id = ?, category_id = ?, note = ? WHERE note_id = ?",
                       (dict['key_title'], dict['key_note_source'], dict['key_is_public'],
                        dict['key_teacher_id'], dict['key_category_id'], dict['key_note'], note_id))
        self.conn_db.commit()

    def delete_note(self, note_id):
        cursor = self.get_cursor()
        query = "DELETE FROM notes WHERE note_id = ?"
        cursor.execute(query, (note_id,))
        self.conn_db.commit()
