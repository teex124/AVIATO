import pyodbc
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = pyodbc.connect(
            "Driver={SQL Server};"
            "Server=KOMPUTER;"
            "Database=AVIATO_DB;"
        )
        self.cursor = self.conn.cursor()

    def execute(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Database error: {str(e)}")
            return False

    def fetch_one(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Database error: {str(e)}")
            return None

    def fetch_all(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Database error: {str(e)}")
            return []

    def close(self):
        if self.conn:
            self.conn.close()

class UserRepository:
    def __init__(self, db):
        self.db = db

    def create_user(self, email, password, wallet_address):
        query = """
            INSERT INTO users (email, password, wallet_address, created_at)
            VALUES (?, ?, ?, ?)
        """
        return self.db.execute(query, (email, password, wallet_address, datetime.now()))

    def get_user_by_email(self, email):
        query = "SELECT * FROM users WHERE email = ?"
        return self.db.fetch_one(query, (email,))

    def get_user_by_wallet(self, wallet_address):
        query = "SELECT * FROM users WHERE wallet_address = ?"
        return self.db.fetch_one(query, (wallet_address,))

    def update_balance(self, wallet_address, new_balance):
        query = "UPDATE users SET balance = ? WHERE wallet_address = ?"
        return self.db.execute(query, (new_balance, wallet_address))

    def get_balance(self, wallet_address):
        query = "SELECT balance FROM users WHERE wallet_address = ?"
        result = self.db.fetch_one(query, (wallet_address,))
        return result[0] if result else 0.0

class HashRepository:
    def __init__(self, db):
        self.db = db

    def get_current_difficulty(self):
        query = "SELECT TOP 1 difficulty FROM mining_difficulty ORDER BY created_at DESC"
        result = self.db.fetch_one(query)
        return result[0] if result else 1.0

    def increase_difficulty(self):
        current = self.get_current_difficulty()
        new_difficulty = current * 1.1
        query = """
            INSERT INTO mining_difficulty (difficulty, created_at)
            VALUES (?, ?)
        """
        return self.db.execute(query, (new_difficulty, datetime.now()))

def connection():
    return pyodbc.connect(
        "Driver={SQL Server};"
        "Server=KOMPUTER;"
        "Database=AVIATO_DB;"
    ) 