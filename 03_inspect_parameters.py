import sqlite3
import json

DATABASE = "output/drone_database.db"

connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

message_types = [
    "GPS",
    "IMU",
    "BARO",
    "ATT",
    "BAT",
    "VIBE",
    "RCIN",
    "RCOU",
    "POS"
]

for message_type in message_types:

    print("\n" + "=" * 50)
    print("MESSAGE TYPE:", message_type)
    print("=" * 50)

    cursor.execute("""
        SELECT data
        FROM log_messages
        WHERE message_type = ?
        LIMIT 1
    """, (message_type,))

    result = cursor.fetchone()

    if result:

        data = json.loads(result[0])

        print("Available parameters:")

        for key, value in data.items():
            print(f"  {key} = {value}")

    else:
        print("No data found.")

connection.close()

print("\nInspection completed! ")