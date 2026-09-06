import sqlite3
import json
import pandas as pd
import os

DATABASE = "output/drone_database.db"
OUTPUT_FILE = "output/flight1_clean.csv"

# --------------------------------------------------
# Connect to database
# --------------------------------------------------

connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

print("==========================================")
print("     CREATING CLEAN DRONE DATASET")
print("==========================================")
print()

# --------------------------------------------------
# Function to read messages
# --------------------------------------------------

def get_messages(message_type):

    cursor.execute("""
        SELECT time_us, data
        FROM log_messages
        WHERE message_type = ?
        ORDER BY time_us
    """, (message_type,))

    rows = cursor.fetchall()

    data_list = []

    for time_us, data in rows:

        try:
            record = json.loads(data)
            record["TimeUS"] = time_us
            data_list.append(record)

        except Exception:
            continue

    return pd.DataFrame(data_list)


# --------------------------------------------------
# Read required message types
# --------------------------------------------------

print("Reading GPS data...")
gps = get_messages("GPS")

print("Reading ATT data...")
att = get_messages("ATT")

print("Reading BAT data...")
bat = get_messages("BAT")

print("Reading VIBE data...")
vibe = get_messages("VIBE")

print("Reading IMU data...")
imu = get_messages("IMU")

print("Reading POS data...")
pos = get_messages("POS")

print()
print("Data loaded successfully!")
print()

# --------------------------------------------------
# Select required columns
# --------------------------------------------------

gps_columns = [
    "TimeUS",
    "Lat",
    "Lng",
    "Alt",
    "Spd",
    "NSats",
    "HDop"
]

att_columns = [
    "TimeUS",
    "Roll",
    "Pitch",
    "Yaw"
]

bat_columns = [
    "TimeUS",
    "Volt",
    "Curr",
    "RemPct"
]

vibe_columns = [
    "TimeUS",
    "VibeX",
    "VibeY",
    "VibeZ",
    "Clip"
]

imu_columns = [
    "TimeUS",
    "GyrX",
    "GyrY",
    "GyrZ",
    "AccX",
    "AccY",
    "AccZ"
]

pos_columns = [
    "TimeUS",
    "RelHomeAlt",
    "RelOriginAlt"
]

# Keep only columns that actually exist
gps = gps[[c for c in gps_columns if c in gps.columns]]
att = att[[c for c in att_columns if c in att.columns]]
bat = bat[[c for c in bat_columns if c in bat.columns]]
vibe = vibe[[c for c in vibe_columns if c in vibe.columns]]
imu = imu[[c for c in imu_columns if c in imu.columns]]
pos = pos[[c for c in pos_columns if c in pos.columns]]

# --------------------------------------------------
# Rename columns
# --------------------------------------------------

gps = gps.rename(columns={
    "Alt": "GPS_Altitude",
    "Spd": "Speed",
    "NSats": "Satellites",
    "HDop": "HDOP"
})

att = att.rename(columns={
    "Roll": "Roll",
    "Pitch": "Pitch",
    "Yaw": "Yaw"
})

bat = bat.rename(columns={
    "Volt": "Battery_Voltage",
    "Curr": "Battery_Current",
    "RemPct": "Battery_Percent"
})

# --------------------------------------------------
# Convert TimeUS to seconds
# --------------------------------------------------

for df in [gps, att, bat, vibe, imu, pos]:

    if "TimeUS" in df.columns:
        df["TimeUS"] = pd.to_numeric(
            df["TimeUS"],
            errors="coerce"
        )

        df["TimeUS"] = df["TimeUS"] / 1_000_000


# --------------------------------------------------
# Rename time column
# --------------------------------------------------

gps = gps.rename(columns={"TimeUS": "Time"})
att = att.rename(columns={"TimeUS": "Time"})
bat = bat.rename(columns={"TimeUS": "Time"})
vibe = vibe.rename(columns={"TimeUS": "Time"})
imu = imu.rename(columns={"TimeUS": "Time"})
pos = pos.rename(columns={"TimeUS": "Time"})


# --------------------------------------------------
# Merge all data using nearest timestamp
# --------------------------------------------------

print("Combining parameters...")

base = gps.sort_values("Time")

for name, df in [
    ("ATT", att),
    ("BAT", bat),
    ("VIBE", vibe),
    ("IMU", imu),
    ("POS", pos)
]:

    if not df.empty:

        df = df.sort_values("Time")

        base = pd.merge_asof(
            base,
            df,
            on="Time",
            direction="nearest"
        )


# --------------------------------------------------
# Remove duplicate columns
# --------------------------------------------------

base = base.loc[:, ~base.columns.duplicated()]


# --------------------------------------------------
# Calculate total vibration
# --------------------------------------------------

if all(col in base.columns for col in ["VibeX", "VibeY", "VibeZ"]):

    base["Vibration_Total"] = (
        base["VibeX"]**2 +
        base["VibeY"]**2 +
        base["VibeZ"]**2
    ) ** 0.5


# --------------------------------------------------
# Calculate total acceleration
# --------------------------------------------------

if all(col in base.columns for col in ["AccX", "AccY", "AccZ"]):

    base["Acceleration_Total"] = (
        base["AccX"]**2 +
        base["AccY"]**2 +
        base["AccZ"]**2
    ) ** 0.5


# --------------------------------------------------
# Save CSV
# --------------------------------------------------

os.makedirs("output", exist_ok=True)

base.to_csv(
    OUTPUT_FILE,
    index=False
)

connection.close()


# --------------------------------------------------
# Final information
# --------------------------------------------------

print()
print("==========================================")
print("       CLEAN DATASET CREATED!")
print("==========================================")
print()

print("Rows:", len(base))
print("Columns:", len(base.columns))

print()
print("Columns available:")

for column in base.columns:
    print("-", column)

print()
print("CSV file:")
print(OUTPUT_FILE)

print()
print("TASK 2 COMPLETED! ")