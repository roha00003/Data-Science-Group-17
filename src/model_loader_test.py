import pandas as pd
import joblib
import os
import numpy as np

# 🔧 Einstellung
INPUT_CSV = "/Users/robin/CodeProjects/Data-Science/data/test_data.csv"
OVERVIEW_CSV = "../saved_models/model_overview.csv"
CAT_FEATURES = ['CCSR Procedure Code', 'Age Group', 'Gender', 'Race', 'Ethnicity']

# 📥 Eingabedaten laden
input_df = pd.read_csv(INPUT_CSV, dtype=str).fillna("").head()
overview_df = pd.read_csv(OVERVIEW_CSV, dtype=str)
# make a dictionary from sets of features to model filenames
model_dict = {}
for _, row in overview_df.iterrows():
    row['features'] = row['features'].replace("'", "").replace("[", "").replace("]", "")
    features_set = set(row['features'].split(', '))
    model_dict[frozenset(features_set)] = row['model_path']

# 🔁 Zeile für Zeile vorhersagen
results = []

for idx, row in input_df.iterrows():
    # 🧠 Nur die vorhandenen Features auswählen
    present_features = [feat for feat in CAT_FEATURES if row[feat] != ""]

    if 'CCSR Procedure Code' not in present_features:
        print(f"❌ Zeile {idx + 1}: Kein 'CCSR Procedure Code' vorhanden. Übersprungen.")
        continue

    # 🔍 Modell finden
    model_features = frozenset(present_features)
    model_path = model_dict.get(model_features)
    if not model_path:
        print(f"❌ Kein Modell gefunden für Zeile {idx + 1}: {present_features}")
        results.append({
            **row.to_dict(),
            "error": "Model not found for these features"
        })
        continue


    if not os.path.exists(model_path):
        print(f"⚠️ Modell nicht gefunden für Zeile {idx + 1}: {present_features}")
        results.append({
            **row.to_dict(),
            "error": f"Model {model_path} not found"
        })
        continue

    # 📦 Modell laden
    bundle = joblib.load(model_path)
    model = bundle["model"]
    encoder = bundle["encoder"]
    features = bundle["features"]
    mortality_encoder = bundle["mortality_encoder"]

    print(features)

    # 🔄 Input encodieren
    # 🧪 Eingabe: row (z. B. aus test.csv als dict)
    input_row_df = pd.DataFrame([row])

    # 🔢 Original-Spalten extrahieren, die beim Training encodiert wurden
    encoder_input_features = encoder.feature_names_in_
    input_row_df = input_row_df[[col for col in encoder_input_features if col in input_row_df.columns]]

    # 🔄 One-Hot-Encoding
    input_encoded_arr = encoder.transform(input_row_df)
    input_encoded_df = pd.DataFrame(input_encoded_arr, columns=encoder.get_feature_names_out())

    # 📈 Vorhersage
    pred = model.predict(input_encoded_df)
    pred = np.array(pred).reshape(1, -1)
    # pred[:, 3] = mortality_encoder.inverse_transform(np.round(pred[:, 3]).astype(int))  # decode mortality

    results.append({
        **row.to_dict(),
        "Predicted Total Costs": pred[0, 0],
        "Predicted Total Charges": pred[0, 1],
        "Predicted Length of Stay": pred[0, 2],
        "Predicted APR Risk of Mortality": mortality_encoder.inverse_transform([int(pred[0, 3])])[0],
    })

# 💾 Ergebnisse speichern
pd.DataFrame(results).to_csv("../temp/predictions_output.csv", index=False)
print("✅ Vorhersagen gespeichert in: predictions_output.csv")