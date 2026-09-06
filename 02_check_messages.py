import sqlite3

DATABASE = "output/drone_database.db"

connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

query = """
SELECT message_type, COUNT(*) AS total_records
FROM log_messages
GROUP BY message_type
ORDER BY total_records DESC
"""

cursor.execute(query)

results = cursor.fetchall()

print("====================================")
print("       DRONE LOG MESSAGE TYPES")
print("====================================")
print()

for message_type, count in results:
    print(f"{message_type:15} {count}")

connection.close()

print()
print("Task 2 - Step 1 completed! ")