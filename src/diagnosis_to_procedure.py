import pickle
import pandas as pd

df = pd.read_csv("../data/data.csv", dtype=str, low_memory=False)

# number of unique CCSR Procedure Codes
unique_procedure_codes = df['CCSR Procedure Code'].nunique()

# Create a dictionary to store the mapping
diagnosis_to_procedure_dict = {}

# Iterate over unique CCSR Diagnosis Code values
for diagnosis_code in df['CCSR Diagnosis Code'].unique():
    # Filter rows for the current diagnosis code
    subset = df[df['CCSR Diagnosis Code'] == diagnosis_code]
    # Get unique CCSR Procedure Code values
    procedure_codes = subset['CCSR Procedure Code'].unique().tolist()

    # remove every procedure code that is used less than 10% of the time for this specific diagnosis code
    threshold = 0.05 * len(subset)
    procedure_codes_res = []
    for code in procedure_codes:
        if (subset['CCSR Procedure Code'] == code).sum() >= threshold:
            procedure_codes_res.append((code, (subset['CCSR Procedure Code'] == code).sum() / len(subset), (subset['CCSR Procedure Code'] == code).median()))


    diagnosis_to_procedure_dict[diagnosis_code] = procedure_codes_res

# Save the dictionary to a file
with open('../data/diagnosis_to_procedure_dict.pkl', 'wb') as file:
    pickle.dump(diagnosis_to_procedure_dict, file)