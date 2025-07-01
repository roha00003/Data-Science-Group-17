import shutil

import pandas as pd
import os

ROOT_PATH = "/Users/robin/PycharmProjects/Data-Science-Group-17"

SAVED_MODELS_PATH = f"{ROOT_PATH}/saved_models_combined"
if not os.path.exists(SAVED_MODELS_PATH):
    os.makedirs(SAVED_MODELS_PATH)
else:
    # remove all files in the directory
    for file in os.listdir(SAVED_MODELS_PATH):
        file_path = os.path.join(SAVED_MODELS_PATH, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

OVERVIEW_CSV = f"{ROOT_PATH}/saved_models_combined/model_overview.csv"
with open(OVERVIEW_CSV, 'w') as f:
    f.write("features,model_path\n")


model_directorys = ["saved_models_filtered_rf_final_7_warning", "saved_models_filtered_rf_final"]

dfs = []
for model_directory in model_directorys:
    overview_csv = f"{ROOT_PATH}/{model_directory}/model_overview.csv"
    df = pd.read_csv(overview_csv, dtype=str)
    df['model_directory'] = model_directory
    dfs.append(df)

# now go over all rows for each model feature set and then copy the model with the highest "Total Costs_r2"
features = []
for df in dfs:
    if "features" in df.columns:
        features.extend(df["features"].unique().tolist())
features = list(set(features))  # Remove duplicates

for feat in features:
    highest_r2 = 0
    highest_model_path = None
    for df in dfs:
        if feat not in df['features'].unique():
            continue
        row = df[df['features'] == feat].iloc[0]
        if float(row['Total Costs_r2']) > highest_r2:
            highest_r2 = float(row['Total Costs_r2'])
            highest_model_path = row['model_path']
    if highest_model_path:
        # Copy the model file to the new directory
        src_path = os.path.join(ROOT_PATH, highest_model_path.replace("../", ""))
        dest_path = os.path.join(SAVED_MODELS_PATH, os.path.basename(highest_model_path))
        if not os.path.exists(dest_path):
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy(src_path, dest_path)
            # write the feature and the path to overview csv not more
            with open(OVERVIEW_CSV, 'a') as f:
                f.write(f"\"{str(feat)}\",{str(dest_path)}\n")
            print(f"Copied {highest_model_path} to {dest_path}")
        else:
            print(f"Model already exists: {dest_path}")