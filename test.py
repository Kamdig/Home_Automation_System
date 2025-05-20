import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute ('''
	CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT UNIQUE NOT NULL,
		password TEXT NOT NULL
	)
''')

cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "password123"))
conn.commit()
conn.close()
