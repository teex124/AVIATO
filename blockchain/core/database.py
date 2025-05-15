import pyodbc
from typing import Optional, List, Tuple
import random

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.connection_string = (
            "Driver={SQL Server};"
            "Server=KOMPUTER;"
            "Database=AVIATO_DB;"
        )
    
    def get_connection(self) -> Optional[pyodbc.Connection]:
        try:
            return pyodbc.connect(self.connection_string)
        except Exception as e:
            print(f"Database connection error: {str(e)}")
            return None

class UserRepository:
    def __init__(self, db: Database):
        self.db = db
    
    def get_user_by_words(self, words: List[str]) -> Optional[Tuple[str, str]]:
        """Get user by their seed words"""
        conn = self.db.get_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT word_indexes, wallet, balance FROM pay_users")
            users = cursor.fetchall()
            
            for user in users:
                stored_indexes = user[0].split(',')
                stored_words = set()
                for index in stored_indexes:
                    cursor.execute(f'SELECT word FROM russian WHERE word_id = {index}')
                    stored_word = cursor.fetchone()[0]
                    stored_words.add(stored_word)
                
                if set(words).issubset(stored_words):
                    return user[1], ','.join(stored_indexes)
            return None
        finally:
            cursor.close()
            conn.close()
    
    def create_user(self, word_indexes: List[int], wallet: str) -> bool:
        """Create new user with seed words and wallet"""
        conn = self.db.get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO pay_users (word_indexes, wallet, balance) VALUES (?, ?, ?)",
                [','.join(map(str, word_indexes)), wallet, 0.0]
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_balance(self, wallet: str) -> float:
        """Get user's balance"""
        conn = self.db.get_connection()
        if not conn:
            return 0.0
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM pay_users WHERE wallet = ?", [wallet])
            result = cursor.fetchone()
            return float(result[0]) if result else 0.0
        finally:
            cursor.close()
            conn.close()

    def update_balance(self, wallet: str, new_balance: float) -> bool:
        """Update user's balance"""
        conn = self.db.get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE pay_users SET balance = ? WHERE wallet = ?",
                [new_balance, wallet]
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating balance: {str(e)}")
            return False
        finally:
            cursor.close()
            conn.close()

class HashRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_current_difficulty(self) -> int:
        """Get current mining difficulty"""
        conn = self.db.get_connection()
        if not conn:
            return 1
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT TOP 1 hash_strong FROM hash_strong ORDER BY hash_strong_id DESC")
            result = cursor.fetchone()
            return int(result[0]) if result else 1
        finally:
            cursor.close()
            conn.close()

    def increase_difficulty(self) -> bool:
        """Increase mining difficulty"""
        conn = self.db.get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            current_difficulty = self.get_current_difficulty()
            new_difficulty = current_difficulty + 1
            cursor.execute(
                "INSERT INTO hash_strong (hash_strong) VALUES (?)",
                [new_difficulty]
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error increasing difficulty: {str(e)}")
            return False
        finally:
            cursor.close()
            conn.close()

class WordRepository:
    def __init__(self, db: Database):
        self.db = db
    
    def get_random_word(self) -> Optional[Tuple[int, str]]:
        """Get random word from dictionary"""
        conn = self.db.get_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            word_id = random.randint(1, 1000000)
            cursor.execute(f'SELECT word FROM russian WHERE word_id = {word_id}')
            result = cursor.fetchone()
            return (word_id, result[0]) if result else None
        finally:
            cursor.close()
            conn.close() 