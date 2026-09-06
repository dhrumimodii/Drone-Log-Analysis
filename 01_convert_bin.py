from pymavlink import DFReader
import sqlite3
import os
import json

# --------------------------------------------------
# 1. File locations
# --------------------------------------------------

BIN_FILE = "log/flight1.BIN"
DATABASE = "output/drone_database.db"

os.makedirs("output", exist_ok=True)

# Check BIN file
if not os.path.exists(BIN_FILE):
    print("ERROR: BIN file not found!")
    print("Expected location:", BIN_FILE)
    exit()

print("====================================")
print("     DRONE LOG ANALYTICS")
print("====================================")
print()

print("Reading drone log...")
print("File:", BIN_FILE)
print()

# --------------------------------------------------
# 2. Read BIN file
# --------------------------------------------------

log = DFReader.DFReader_binary(BIN_FILE)

print("BIN file opened successfully!")
print("Converting data into database...")
print()

# --------------------------------------------------
# 3. Create SQLite database
# --------------------------------------------------

connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS log_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_type TEXT,
    time_us REAL,
    data TEXT
)
""")

# --------------------------------------------------
# 4. Function to convert bytes
# --------------------------------------------------

def convert_bytes(obj):
    if isinstance(obj, bytes):
        return obj.hex()

    if isinstance(obj, dict):
        return {
            key: convert_bytes(value)
            for key, value in obj.items()
        }

    if isinstance(obj, list):
        return [
            convert_bytes(value)
            for value in obj
        ]

    return obj


# --------------------------------------------------
# 5. Read every message
# --------------------------------------------------

count = 0

while True:

    msg = log.recv_msg()

    if msg is None:
        break

    message_type = msg.get_type()

    if message_type == "BAD_DATA":
        continue

    try:
        data = msg.to_dict()

        # Convert bytes into JSON-compatible text
        data = convert_bytes(data)

    except Exception:
        continue

    time_us = data.get("TimeUS", None)

    cursor.execute(
        """
        INSERT INTO log_messages
        (message_type, time_us, data)
        VALUES (?, ?, ?)
        """,
        (
            message_type,
            time_us,
            json.dumps(data)
        )
    )

    count += 1

    if count % 10000 == 0:
        print("Processed records:", count)

# --------------------------------------------------
# 6. Save database
# --------------------------------------------------

connection.commit()
connection.close()

print()
print("====================================")
print("       CONVERSION COMPLETED!")
print("====================================")
print()

print("Total records:", count)
print("Database created:", DATABASE)

print()
print("TASK 1 COMPLETED SUCCESSFULLY! ")