import sqlite3

conn = sqlite3.connect('database/resume.db')

cursor = conn.cursor()

try:
    cursor.execute(
        "ALTER TABLE resumes ADD COLUMN score INTEGER DEFAULT 0"
    )

    print("Score column added!")

except:
    print("Score column already exists!")

conn.commit()
conn.close()