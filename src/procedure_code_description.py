import pickle
import pandas as pd

df = pd.read_csv("../data/data.csv", dtype=str, low_memory=False)

# number of unique CCSR Procedure Codes
unique_procedure_codes = df['CCSR Procedure Code'].unique()

# Create a dictionary to store the mapping
code_to_description_dict = {}

# Iterate over unique CCSR Diagnosis Code values
for code in unique_procedure_codes:
    subset = df[df['CCSR Procedure Code'] == code]
    descriptions = subset['CCSR Procedure Description'].unique().tolist()
    assert len(descriptions) == 1, f"Multiple descriptions found for code {code}: {description}"
    description = descriptions[0] + " (" + code + ")"


# Save the dictionary to a file
with open('../data/procedure_code_to_description_dict.pkl', 'wb') as file:
    pickle.dump(code_to_description_dict, file)