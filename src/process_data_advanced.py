import pandas as pd

trashhold = 0.97

# CSV-Datei einlesen
df = pd.read_csv("output\data\preprocess_data.csv")

# Zählen, wie oft jede Prozedur je Diagnose vorkommt
counts = df.groupby(["CCSR Diagnosis Code", "CCSR Procedure Code"]).size().reset_index(name="count")

# Prozentuale Anteile je Diagnose berechnen
counts["percent"] = counts.groupby("CCSR Diagnosis Code")["count"].transform(lambda x: x / x.sum())

# Kumulative Anteile berechnen
counts["cumulative_percent"] = counts.groupby("CCSR Diagnosis Code")["percent"].cumsum()

# Nur Prozeduren behalten, deren kumulierter Anteil ≤ 97 % ist
top_procedures = counts[counts["cumulative_percent"] <= trashhold][["CCSR Diagnosis Code", "CCSR Procedure Code"]]

# DataFrame darauf filtern
df_filtered = df.merge(top_procedures, on=["CCSR Diagnosis Code", "CCSR Procedure Code"], how="inner")

df_filtered.to_csv("output/data/data.csv", index=False)