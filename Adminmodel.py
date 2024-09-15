from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3


class Adminpanel():
    def __init__(self):
        self.db = 'databases/testgpt.db'
        self.conn_db = sqlite3.connect(self.db)

    def get_cursor(self):
        cursor = self.conn_db.cursor()
        cursor.row_factory = sqlite3.Row
        return cursor

    def get_categories(self):
        cursor = self.get_cursor()
        query = """SELECT teacher_id, display_name, username, date_created, is_admin FROM teachers"""
        cursor.execute(query)
        return cursor.fetchall()

    def get_one_category(self, category_id):
        cursor = self.get_cursor()
        query = "SELECT omschrijving FROM categories WHERE category_id = ?"
        cursor.execute(query, (category_id))
        return cursor.fetchone()

    def create_category(self, new_category):
        cursor = self.get_cursor()
        query = """INSERT INTO teachers (omschrijving) VALUES (?)"""
        cursor.execute(query, (new_category,))
        self.conn_db.commit()

    def change_category(self, category_id, new_category):
        cursor = self.get_cursor()
        query = """UPDATE categories SET omschrijving = ? WHERE category_id = ?"""
        cursor.execute(query, (new_category, category_id))
        self.conn_db.commit()


class AddTeacher():
    def __init__(self):
        self.db = 'databases/testgpt.db'
        self.conn_db = sqlite3.connect(self.db)

    def get_cursor(self):
        cursor = self.conn_db.cursor()
        cursor.row_factory = sqlite3.Row
        return cursor

    def create_teacher(self, hashed_password, display_name, username, is_admin):
        conn = sqlite3.connect('databases/testgpt.db')
        cursor = conn.cursor()
        query = "INSERT INTO teachers (teacher_password, display_name, username, is_admin) VALUES (?, ?, ?, ?)"
        values = (hashed_password, display_name, username, is_admin)
        cursor.execute(query, values)
        cursor.fetchall()
        conn.commit()
        conn.close()
        return cursor
