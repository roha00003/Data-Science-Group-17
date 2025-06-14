import pandas as pd

def clean_costs(series):
    return pd.to_numeric(series.astype(str).str.replace(",", ""), errors='coerce')

# CSV-Datei einlesen
df = pd.read_csv("data\Topic 4\Hospital_Inpatient_Discharges__SPARCS_De-Identified___2022_20250423.csv")

# Nicht benötigte Spalten entfernen
df = df.drop(columns=["Hospital Service Area","Hospital County","Operating Certificate Number","Permanent Facility Id","Facility Name","Zip Code - 3 digits","Patient Disposition","Discharge Year","APR DRG Code","APR DRG Description","APR MDC Code","APR MDC Description","APR Severity of Illness Code","APR Severity of Illness Description","APR Medical Surgical Description","Payment Typology 1","Payment Typology 2","Payment Typology 3","Birth Weight","Emergency Department Indicator"])

# Zeilen entfernen, bei denen 'Type of Admission' == 'Newborn'
df = df[df["Type of Admission"] != "Newborn"]

# Nach 'Diagnose' und dann nach 'Prozedur' sortieren
df = df.sort_values(by=["CCSR Diagnosis Code", "CCSR Procedure Code"])

# Spaltenreihenfolge: 'Diagnose' und 'Prozedur' zuerst
cols = df.columns.tolist()
new_order = [col for col in ["CCSR Diagnosis Code", "CCSR Procedure Code"] if col in cols] + [col for col in cols if col not in ["CCSR Diagnosis Code", "CCSR Procedure Code"]]
df = df[new_order]

# 'Total Charges'-Spalte bereinigen
df["Total Charges"] = clean_costs(df["Total Charges"])
# 'Total Costs'-Spalte bereinigen
df["Total Costs"] = clean_costs(df["Total Costs"])

# Optional: Sortiertes DataFrame speichern
df.to_csv("output/data/preprocess_data.csv", index=False)