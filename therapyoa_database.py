import sqlite3

# Connect to the database or create a new one if it doesn't exist
conn = sqlite3.connect('client_database.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Create a table to store client information
cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        date_of_birth TEXT NOT NULL,
        ahcccs_id TEXT NOT NULL
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()