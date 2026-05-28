import sqlite3

conn = sqlite3.connect('database/resume.db')
cursor = conn.cursor()

try:
    cursor.execute(
        "ALTER TABLE resumes ADD COLUMN role TEXT"
    )
except:
    pass

conn.commit()
conn.close()

print("Database Updated!")