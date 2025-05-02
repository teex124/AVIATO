import pyodbc

def connection():
    try:
        return pyodbc.connect(
            "Driver={SQL Server};"
            "Server=KOMPUTER;"
            "Database=AVIATO_DB;" 
        )
    except Exception as e: 
        return None


def read_data(table_name):
    cursor = connection().cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        return rows
    except:
        return None

def insert_data(table_name, data_dict,columns):
    conn = connection()
    if conn is None:
        return None
        
    cursor = conn.cursor()
    try: 
        placeholders = ", ".join(["?" for _ in data_dict])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        cursor.execute(query, data_dict)
        conn.commit() 
        return True
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()