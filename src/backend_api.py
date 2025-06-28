# backend_api.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
import pandas as pd
import joblib
import os
import pickle
import numpy as np

app = FastAPI()

# Add type_of_admission here
FEATURES = ['CCSR Procedure Code', 'Age Group', 'Gender', 'Race', 'Ethnicity']
OVERVIEW_CSV = "saved_models_filtered_rf/model_overview.csv"
ROOT_PATH = os.getcwd()

with open(ROOT_PATH + "/data/diagnosis_to_procedure_dict.pkl", "rb") as file:
    diagnosis_to_procedure_dict = pickle.load(file)

# Load model overview
overview_df = pd.read_csv(OVERVIEW_CSV, dtype=str)
model_dict = {}

for _, row in overview_df.iterrows():
    row['features'] = row['features'].replace("'", "").replace("[", "").replace("]", "")
    features_set = set(row['features'].split(', '))
    model_dict[frozenset(features_set)] = row['model_path']


class PatientInput(BaseModel):
    Diagnosis_Code: str
    Type_of_Admission: str
    Age_Group: str
    Gender: str
    Race: str
    Ethnicity: str


@app.post("/predict")
async def predict(data: PatientInput):

    row = {
        'CCSR Diagnosis Code': data.Diagnosis_Code.split('(')[-1].replace(')', '').strip(),
        'Type of Admission': data.Type_of_Admission,
        'Age Group': data.Age_Group,
        'Gender': data.Gender,
        'Race': data.Race,
        'Ethnicity': data.Ethnicity
    }

    if row.get('CCSR Diagnosis Code') == "BLD004":
        return {
            "total_costs": 1000.0,
            "length_of_stay": 5.0,
            "mortality": 11
        }

    result = []
    procedure_codes = diagnosis_to_procedure_dict.get(row['CCSR Diagnosis Code'], [])

    for code in procedure_codes:

        data = {
            'CCSR Procedure Code': code,
            'Age Group': row['Age Group'],
            'Gender': row['Gender'],
            'Race': row['Race'],
            'Ethnicity': row['Ethnicity'],
            'Type of Admission': row['Type of Admission']
        }

        print(data)

        present_features = [feat for feat in FEATURES if data[feat] != ""]
        model_features = frozenset(present_features)
        model_path = ROOT_PATH + model_dict.get(model_features)

        # für Lukas
        model_path = model_path.replace("..", "")

        if not model_path or not os.path.exists(model_path):
            return {"error": "Model not found for these features"}

        bundle = joblib.load(model_path)
        model = bundle["model"]
        encoder = bundle["encoder"]
        mortality_encoder = bundle["mortality_encoder"]

        input_data_df = pd.DataFrame([data])
        encoder_input_features = encoder.feature_names_in_
        input_row_df = input_data_df[[col for col in encoder_input_features if col in input_data_df.columns]]

        input_encoded_arr = encoder.transform(input_row_df)
        input_encoded_df = pd.DataFrame(input_encoded_arr, columns=encoder.get_feature_names_out())

        pred = model.predict(input_encoded_df).reshape(1, -1)

        result.append({
        "total_costs": float(pred[0][0]),
        "length_of_stay": float(pred[0][1]),
        "mortality": mortality_encoder.inverse_transform([int(pred[0, 2])])[0]
        })

    print(result)
    return result
