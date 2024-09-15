import sqlite3
import os
import re

class CategoryModel():
    def __init__(self):
        self.db = 'databases/testgpt.db'
        self.conn_db = sqlite3.connect(self.db)

    def get_cursor(self):
        cursor = self.conn_db.cursor()
        cursor.row_factory = sqlite3.Row
        return cursor

    def get_categories(self):
        cursor = self.get_cursor()
        query = """SELECT category_id, omschrijving FROM categories
                    ORDER BY omschrijving ASC"""
        cursor.execute(query)
        return cursor.fetchall()
    
    def get_one_category(self, category_id):
        cursor = self.get_cursor()
        query = "SELECT omschrijving FROM categories WHERE category_id = ?"
        cursor.execute(query, (category_id))
        return cursor.fetchone()
    
    def create_category(self, new_category):
        cursor = self.get_cursor()
        query = """INSERT INTO categories (omschrijving) VALUES (?)"""
        cursor.execute(query, (new_category,))
        self.conn_db.commit()

    def change_category(self, category_id, new_category):
        cursor = self.get_cursor()
        query = """UPDATE categories SET omschrijving = ? WHERE category_id = ?"""
        cursor.execute(query, (new_category, category_id))
        self.conn_db.commit()