from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import os
import pickle

app = FastAPI()

# Add type_of_admission here
FEATURES = ['CCSR Procedure Code', 'Age Group', 'Gender', 'Race', 'Ethnicity', 'Type of Admission']
OVERVIEW_CSV = "model/model_overview.csv"
ROOT_PATH = os.getcwd() #+ "/Backend" # Adjust the path as necessary

with open(ROOT_PATH + "/data/diagnosis_to_procedure_dict.pkl", "rb") as file:
    diagnosis_to_procedure_dict = pickle.load(file)

with open(ROOT_PATH + "/data/procedure_code_to_description_dict.pkl", "rb") as file:
    procedure_code_to_description_dict = pickle.load(file)

# Load model overview
overview_df = pd.read_csv(OVERVIEW_CSV, dtype=str)
model_dict = {}

for _, row in overview_df.iterrows():
    row['features'] = row['features'].replace("'", "").replace("[", "").replace("]", "")
    features_set = set(row['features'].split(', '))
    model_dict[frozenset(features_set)] = row['model_path']


class PatientInput(BaseModel):
    Diagnosis_Code: str
    Age_Group: str
    Gender: str
    Race: str
    Ethnicity: str
    Type_of_Admission: str


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

    result = []
    procedure_codes = diagnosis_to_procedure_dict.get(row['CCSR Diagnosis Code'], [])

    for code, percentage, median in procedure_codes:

        data = {
            'CCSR Procedure Code': code,
            'Age Group': row['Age Group'],
            'Gender': row['Gender'],
            'Race': row['Race'],
            'Ethnicity': row['Ethnicity'],
            'Type of Admission': row['Type of Admission']
        }


        present_features = [feat for feat in FEATURES if data[feat] != ""]
        model_features = frozenset(present_features)

        model_path = ROOT_PATH + model_dict.get(model_features)

        # for adjustment
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
            "procedure_code": procedure_code_to_description_dict.get(code, code),
            "total_costs": round(float(pred[0][0]) - percentage * (float(median) - float(pred[0][0])), -2) if round(float(pred[0][0]) - percentage * (float(median) - float(pred[0][0])), -2) >= 0.1 * float(pred[0][0]) else median,  # round to nearest 100
            "length_of_stay": round(float(pred[0][1])),  # round to the nearest whole number
            "mortality": mortality_encoder.inverse_transform([int(round(pred[0, 2]))])[0],
            "usage_percentage": round(percentage * 100, 2),
        })

    number_of_results = 3


    # sort according to costs and usage
    result.sort(key=lambda x: x['total_costs'], reverse=False)
    result = result[:number_of_results]

    def mortality_to_number(mortality):
        if mortality == 'Minor':
            return 1
        elif mortality == 'Moderate':
            return 2
        elif mortality == 'Major':
            return 3
        elif mortality == 'Extreme':
            return 4
        else:
            return 0

    # sort according to mortality
    result.sort(key=lambda x: mortality_to_number(x['mortality']), reverse=True)

    # sort according to the usage percentage
    result.sort(key=lambda x: x['usage_percentage'], reverse=True)

    # sort according to length of stay
    result.sort(key=lambda x: x['length_of_stay'], reverse=True)

    # sort according to total costs
    result.sort(key=lambda x: x['total_costs'], reverse=False)

    # remove mortality from the result
    for item in result:
        del item['mortality']

    return result
