# backend_api.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
import pandas as pd
import joblib
import os
import numpy as np

app = FastAPI()

# Add type_of_admission here
CAT_FEATURES = ['CCSR Procedure Code', 'Age Group', 'Gender', 'Race', 'Ethnicity']
OVERVIEW_CSV = "saved_models/model_overview.csv"

# Load model overview
overview_df = pd.read_csv(OVERVIEW_CSV, dtype=str)
model_dict = {}

for _, row in overview_df.iterrows():
    row['features'] = row['features'].replace("'", "").replace("[", "").replace("]", "")
    features_set = set(row['features'].split(', '))
    model_dict[frozenset(features_set)] = row['model_path']


class PatientInput(BaseModel):
    CCSR_Procedure_Code: str
    Age_Group: str
    Gender: str
    Race: str
    Ethnicity: str


@app.post("/predict")
async def predict(data: PatientInput):
    row = {
        'CCSR Procedure Code': data.CCSR_Procedure_Code,
        'Age Group': data.Age_Group,
        'Gender': data.Gender,
        'Race': data.Race,
        'Ethnicity': data.Ethnicity
    }

    if row.get('CCSR Procedure Code') == "Pneumonia":
        return {
            "total_costs": 1000.0,
            "length_of_stay": 5.0,
            "mortality": 11
        }

    present_features = [feat for feat in CAT_FEATURES if row[feat] != ""]
    model_features = frozenset(present_features)
    model_path = model_dict.get(model_features)

    if not model_path or not os.path.exists(model_path):
        return {"error": "Model not found for these features"}

    bundle = joblib.load(model_path)
    model = bundle["model"]
    encoder = bundle["encoder"]
    mortality_encoder = bundle["mortality_encoder"]

    input_row_df = pd.DataFrame([row])
    encoder_input_features = encoder.feature_names_in_
    input_row_df = input_row_df[[col for col in encoder_input_features if col in input_row_df.columns]]

    input_encoded_arr = encoder.transform(input_row_df)
    input_encoded_df = pd.DataFrame(input_encoded_arr, columns=encoder.get_feature_names_out())

    pred = model.predict(input_encoded_df).reshape(1, -1)

    return {
        "total_costs": float(pred[0][0]),
        "length_of_stay": float(pred[0][1]),
        "mortality": mortality_encoder.inverse_transform([int(pred[0, 3])])[0]
    }
