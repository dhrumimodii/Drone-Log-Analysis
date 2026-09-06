import sqlite3
import json
import re

SOURCE_DB = "output/drone_database.db"
OUTPUT_DB = "output/drone_full_tables.db"


def safe_name(name):
    """Make a safe SQLite table/column name."""
    name = re.sub(r"[^A-Za-z0-9_]", "_", str(name))
    return name if name else "unknown"


def sqlite_type(value):
    """Choose a suitable SQLite data type."""
    if isinstance(value, bool):
        return "INTEGER"
    elif isinstance(value, int):
        return "INTEGER"
    elif isinstance(value, float):
        return "REAL"
    else:
        return "TEXT"


# Open old database
src = sqlite3.connect(SOURCE_DB)
src_cursor = src.cursor()

# Create new database
dst = sqlite3.connect(OUTPUT_DB)
dst_cursor = dst.cursor()

# Get all message types
message_types = [
    row[0]
    for row in src_cursor.execute(
        "SELECT DISTINCT message_type FROM log_messages"
    )
]

print("Message types found:", len(message_types))
print()

total_inserted = 0

for message_type in message_types:

    table_name = safe_name(message_type)

    print("Creating table:", table_name)

    # --------------------------------------------------
    # STEP 1: Find all columns for this message type
    # --------------------------------------------------

    columns = {}

    cursor = src_cursor.execute(
        "SELECT id, data FROM log_messages WHERE message_type = ?",
        (message_type,)
    )

    while True:
        rows = cursor.fetchmany(5000)

        if not rows:
            break

        for record_id, data in rows:

            try:
                record = json.loads(data)
            except Exception:
                continue

            for key, value in record.items():

                key = safe_name(key)

                if key not in columns:
                    columns[key] = sqlite_type(value)

    if not columns:
        continue

    # --------------------------------------------------
    # STEP 2: Create table
    # --------------------------------------------------

    column_definitions = [
        '"record_id" INTEGER PRIMARY KEY'
    ]

    for column, data_type in columns.items():

        if column == "record_id":
            continue

        column_definitions.append(
            f'"{column}" {data_type}'
        )

    create_sql = f"""
    CREATE TABLE IF NOT EXISTS "{table_name}" (
        {", ".join(column_definitions)}
    )
    """

    dst_cursor.execute(create_sql)

    # --------------------------------------------------
    # STEP 3: Insert data
    # --------------------------------------------------

    all_columns = ["record_id"] + [
        c for c in columns if c != "record_id"
    ]

    column_sql = ", ".join(
        f'"{c}"' for c in all_columns
    )

    placeholders = ", ".join(
        ["?"] * len(all_columns)
    )

    insert_sql = f"""
    INSERT OR REPLACE INTO "{table_name}"
    ({column_sql})
    VALUES ({placeholders})
    """

    cursor = src_cursor.execute(
        "SELECT id, data FROM log_messages WHERE message_type = ?",
        (message_type,)
    )

    inserted = 0

    while True:

        rows = cursor.fetchmany(5000)

        if not rows:
            break

        batch = []

        for record_id, data in rows:

            try:
                record = json.loads(data)
            except Exception:
                continue

            values = [record_id]

            for column in all_columns[1:]:

                value = record.get(column)

                # Convert complex values to text
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)

                batch.append if False else None
                values.append(value)

            batch.append(values)

        if batch:
            dst_cursor.executemany(insert_sql, batch)
            inserted += len(batch)

        dst.commit()

    total_inserted += inserted

    print("   Records:", inserted)


# Final commit
dst.commit()

# Close databases
src.close()
dst.close()

print()
print("======================================")
print("FULL DATABASE CREATED SUCCESSFULLY!")
print("======================================")
print("Total records:", total_inserted)
print()
print("Database:")
print(OUTPUT_DB)