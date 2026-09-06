import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# --------------------------------------------------
# 1. Load clean dataset
# --------------------------------------------------

INPUT_FILE = "output/flight1_clean.csv"

df = pd.read_csv(INPUT_FILE)

print("==========================================")
print("       DRONE ANOMALY ANALYSIS")
print("==========================================")
print()

print("Dataset loaded!")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print()

# --------------------------------------------------
# 2. Parameters for anomaly detection
# --------------------------------------------------

parameters = [
    "Speed",
    "GPS_Altitude",
    "Roll",
    "Pitch",
    "Battery_Voltage",
    "Vibration_Total",
    "Acceleration_Total"
]

# --------------------------------------------------
# 3. Calculate Z-score
# --------------------------------------------------

print("Calculating anomaly scores...")
print()

for parameter in parameters:

    if parameter not in df.columns:
        print("Skipping:", parameter)
        continue

    # Convert to numeric
    df[parameter] = pd.to_numeric(
        df[parameter],
        errors="coerce"
    )

    mean = df[parameter].mean()
    std = df[parameter].std()

    if std == 0 or pd.isna(std):
        df[parameter + "_Z"] = 0
    else:
        df[parameter + "_Z"] = (
            (df[parameter] - mean) / std
        )

# --------------------------------------------------
# 4. Flag anomalies
# --------------------------------------------------

threshold = 3

df["Anomaly_Count"] = 0

for parameter in parameters:

    z_column = parameter + "_Z"

    if z_column in df.columns:

        df["Anomaly_Count"] += (
            df[z_column].abs() > threshold
        ).astype(int)

# --------------------------------------------------
# 5. Overall anomaly flag
# --------------------------------------------------

df["Anomaly"] = np.where(
    df["Anomaly_Count"] > 0,
    "ANOMALY",
    "NORMAL"
)

# --------------------------------------------------
# 6. Save analysis dataset
# --------------------------------------------------

OUTPUT_FILE = "output/flight1_analyzed.csv"

df.to_csv(
    OUTPUT_FILE,
    index=False
)

# --------------------------------------------------
# 7. Display results
# --------------------------------------------------

total_anomalies = (
    df["Anomaly"] == "ANOMALY"
).sum()

total_records = len(df)

percentage = (
    total_anomalies / total_records
) * 100

print("==========================================")
print("       ANALYSIS RESULTS")
print("==========================================")
print()

print("Total records:", total_records)
print("Anomalous records:", total_anomalies)
print(
    "Anomaly percentage:",
    round(percentage, 2),
    "%"
)

print()

# --------------------------------------------------
# 8. Count anomalies by parameter
# --------------------------------------------------

print("Anomalies by parameter:")
print()

for parameter in parameters:

    z_column = parameter + "_Z"

    if z_column in df.columns:

        count = (
            df[z_column].abs() > threshold
        ).sum()

        print(
            f"{parameter:25} : {count}"
        )

# --------------------------------------------------
# 9. Save anomaly records
# --------------------------------------------------

anomalies = df[
    df["Anomaly"] == "ANOMALY"
]

anomalies.to_csv(
    "output/anomalies.csv",
    index=False
)

# --------------------------------------------------
# 10. Create output folder for graphs
# --------------------------------------------------

os.makedirs(
    "output/graphs",
    exist_ok=True
)

# --------------------------------------------------
# 11. Create graphs
# --------------------------------------------------

graph_parameters = [
    ("GPS_Altitude", "Altitude"),
    ("Speed", "Speed"),
    ("Vibration_Total", "Vibration"),
    ("Battery_Voltage", "Battery Voltage")
]

for column, title in graph_parameters:

    if column not in df.columns:
        continue

    plt.figure(figsize=(12, 5))

    plt.plot(
        df["Time"],
        df[column]
    )

    # Mark anomalies
    abnormal = df[
        df["Anomaly"] == "ANOMALY"
    ]

    if len(abnormal) > 0:

        plt.scatter(
            abnormal["Time"],
            abnormal[column],
            marker="x",
            label="Anomaly"
        )

    plt.xlabel("Time (seconds)")
    plt.ylabel(title)

    plt.title(
        title + " vs Time"
    )

    plt.legend()
    plt.grid(True)

    filename = (
        "output/graphs/"
        + column
        + "_analysis.png"
    )

    plt.savefig(
        filename,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

print()
print("==========================================")
print("       FILES CREATED")
print("==========================================")
print()

print("Analysis dataset:")
print("output/flight1_analyzed.csv")

print()

print("Anomaly records:")
print("output/anomalies.csv")

print()

print("Graphs:")
print("output/graphs/")

print()
print("TASK 3 COMPLETED! ")