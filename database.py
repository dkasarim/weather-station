import sqlite3
import os
from config import DB_PATH

def get_connection_to_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    """
        Initializes the SQLite database and creates the 'weather' table if it doesn't exist.

        Ensures the database file is always created in the same directory as this script.
        """
    conn = get_connection_to_db()
    cursor = conn.cursor()  # Cursor object to execute commands
 # Creates a table structure
    cursor.execute('''CREATE TABLE IF NOT EXISTS weather (     
                   id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                   timestamp TEXT,
                   city TEXT,
                   state TEXT,
                   temp REAL,
                   pressure INTEGER,
                   humidity INTEGER,
                   clouds INTEGER)
                   ''')

    conn.commit()  # Applies changes to the DB
    conn.close()

if __name__ == "__main__":  # Sets up DB, if running this script directly
    init_db()

