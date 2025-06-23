import pandas as pd
import numpy as np
import itertools
import os
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.metrics import r2_score, mean_squared_error

# 📂 Einstellungen
DATA_PATH = "/Users/robin/CodeProjects/Data-Science/data/Hospital_Inpatient_Discharges__SPARCS_De-Identified___2022_20250423.csv"
MODEL_DIR = "../saved_models"
os.makedirs(MODEL_DIR, exist_ok=True)

# 🎯 Zielvariablen (immer alle)
targets = ['Total Costs', 'Total Charges', 'Length of Stay', 'APR Risk of Mortality']

# 📥 Daten laden
df = pd.read_csv(DATA_PATH, dtype=str, low_memory=False, nrows=10)

# 🧹 Bereinigen
df['Total Costs'] = df['Total Costs'].str.replace(',', '').astype(float)
df['Total Charges'] = df['Total Charges'].str.replace(',', '').astype(float)
df['Length of Stay'] = pd.to_numeric(df['Length of Stay'], errors='coerce')
df = df.dropna(subset=targets)

# 📌 Kategorische Eingabefeatures
cat_features = ['CCSR Procedure Code', 'Age Group', 'Gender', 'Race', 'Ethnicity']
df = df.dropna(subset=cat_features)

# 🔤 Encode Zielspalte APR
mortality_encoder = LabelEncoder()
df['APR Risk of Mortality'] = mortality_encoder.fit_transform(df['APR Risk of Mortality'])

# 🔁 Alle Feature-Kombinationen vorbereiten
optional_features = ['Age Group', 'Gender', 'Race', 'Ethnicity']
base_feature = ['CCSR Procedure Code']
all_combinations = []

for r in range(len(optional_features) + 1):
    for combo in itertools.combinations(optional_features, r):
        all_combinations.append(base_feature + list(combo))

# 📈 Trainiere und speichere pro Kombination
results = []
print("🔁 Starte Multi-Target-Modelltraining...\n")

for features in all_combinations:
    try:
        # Nur Daten, wo alle aktuellen Features vorhanden sind
        current_df = df.dropna(subset=features + targets)

        # 🔤 OneHotEncoder auf aktuellen Feature-Subset
        encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
        X_encoded = encoder.fit_transform(current_df[features])
        X_df = pd.DataFrame(X_encoded, columns=encoder.get_feature_names_out(features))

        y_df = current_df[targets].reset_index(drop=True)

        # 🎯 Modelltraining
        model = MultiOutputRegressor(RandomForestRegressor(n_estimators=100, random_state=42))
        model.fit(X_df, y_df)
        y_pred = model.predict(X_df)

        # 📊 Scores berechnen
        scores = {}
        for i, target in enumerate(targets):
            scores[f"{target}_r2"] = r2_score(y_df.iloc[:, i], y_pred[:, i])
            scores[f"{target}_mse"] = mean_squared_error(y_df.iloc[:, i], y_pred[:, i])

        # 💾 Modell & Encoder speichern
        model_name = f"{'__'.join(f.replace(' ', '_') for f in features)}.pkl"
        model_path = os.path.join(MODEL_DIR, model_name)

        joblib.dump({
            "model": model,
            "features": features,
            "encoder": encoder,
            "target_columns": targets,
            "mortality_encoder": mortality_encoder
        }, model_path)

        print(f"✅ Gespeichert: {model_name}")
        results.append({
            "features": features,
            "model_path": model_path,
            **scores
        })

    except Exception as e:
        print(f"❌ Fehler bei Features {features}: {e}")

# 📄 Zusammenfassung
results_df = pd.DataFrame(results)
results_df.to_csv(os.path.join(MODEL_DIR, "model_overview.csv"), index=False)
print("\n📦 Modelle gespeichert in:", MODEL_DIR)
print("📄 Zusammenfassung als: model_overview.csv")