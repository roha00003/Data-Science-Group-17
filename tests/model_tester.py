import unittest
import os
import pandas as pd
import joblib

class ModelTester(unittest.TestCase):
    model_dict = None
    ROOT_PATH = "/Users/robin/PycharmProjects/Data-Science-Group-17"
    OVERVIEW_CSV = "../saved_models_combined/model_overview.csv"
    sample_input = {
        'CCSR Procedure Code': "ADM001",
        'Age Group': "50 to 69",
        'Gender': "M",
        'Race': "Black/African American",
        'Ethnicity': "Not Span/Hispanic",
        'Type of Admission': "Emergency"
    }

    @classmethod
    def setUpClass(cls):
        overview_df = pd.read_csv(cls.OVERVIEW_CSV, dtype=str)
        cls.model_dict = {}
        for _, row in overview_df.iterrows():
            row['features'] = row['features'].replace("'", "").replace("[", "").replace("]", "")
            features_set = set(row['features'].split(', '))
            cls.model_dict[frozenset(features_set)] = row['model_path']

    def run_model_test(self, feature_names: list):
        feature_set = frozenset(feature_names)
        model_rel_path = self.model_dict.get(feature_set)
        self.assertIsNotNone(model_rel_path, f"No Model for this set: {feature_set}")
        model_path = os.path.join(self.ROOT_PATH, model_rel_path.replace("../", ""))
        self.assertTrue(os.path.exists(model_path), f"Model path does not exist: {model_path}")

        bundle = joblib.load(model_path)
        model = bundle["model"]
        encoder = bundle["encoder"]
        mortality_encoder = bundle["mortality_encoder"]

        df = pd.DataFrame([self.sample_input])
        input_row_df = df[[col for col in encoder.feature_names_in_ if col in df.columns]]
        encoded_arr = encoder.transform(input_row_df)
        encoded_df = pd.DataFrame(encoded_arr, columns=encoder.get_feature_names_out())

        pred = model.predict(encoded_df)
        decoded_mortality = mortality_encoder.inverse_transform([int(round(pred[0, 2]))])[0]
        assert isinstance(decoded_mortality, str), "Mortality decoding did not return a string"

    def test_age_gender_race_ethnicity(self): self.run_model_test(
        ['Age Group', 'Gender', 'Race', 'Ethnicity', 'CCSR Procedure Code', 'Type of Admission'])

    def test_age_gender_race(self): self.run_model_test(
        ['Age Group', 'Gender', 'Race', 'CCSR Procedure Code', 'Type of Admission'])

    def test_age_gender_ethnicity(self): self.run_model_test(
        ['Age Group', 'Gender', 'Ethnicity', 'CCSR Procedure Code', 'Type of Admission'])

    def test_age_race_ethnicity(self): self.run_model_test(
        ['Age Group', 'Race', 'Ethnicity', 'CCSR Procedure Code', 'Type of Admission'])

    def test_gender_race_ethnicity(self): self.run_model_test(
        ['Gender', 'Race', 'Ethnicity', 'CCSR Procedure Code', 'Type of Admission'])

    def test_age_gender(self): self.run_model_test(['Age Group', 'Gender', 'CCSR Procedure Code', 'Type of Admission'])

    def test_age_race(self): self.run_model_test(['Age Group', 'Race', 'CCSR Procedure Code', 'Type of Admission'])

    def test_age_ethnicity(self): self.run_model_test(
        ['Age Group', 'Ethnicity', 'CCSR Procedure Code', 'Type of Admission'])

    def test_gender_race(self): self.run_model_test(['Gender', 'Race', 'CCSR Procedure Code', 'Type of Admission'])

    def test_gender_ethnicity(self): self.run_model_test(
        ['Gender', 'Ethnicity', 'CCSR Procedure Code', 'Type of Admission'])

    def test_race_ethnicity(self): self.run_model_test(
        ['Race', 'Ethnicity', 'CCSR Procedure Code', 'Type of Admission'])

    def test_age_group_only(self): self.run_model_test(['Age Group', 'CCSR Procedure Code', 'Type of Admission'])

    def test_gender_only(self): self.run_model_test(['Gender', 'CCSR Procedure Code', 'Type of Admission'])

    def test_race_only(self): self.run_model_test(['Race', 'CCSR Procedure Code', 'Type of Admission'])

    def test_ethnicity_only(self): self.run_model_test(['Ethnicity', 'CCSR Procedure Code', 'Type of Admission'])

    def test_only_mandatory_features(self): self.run_model_test(['CCSR Procedure Code', 'Type of Admission'])

    def test_missing_mandatory_features_should_fail(self):
        broken_input = {
            'Age Group': "50 to 69",
            'Gender': "M",
            'Race': "Black/African American",
            'Ethnicity': "Not Span/Hispanic",
            # 'CCSR Procedure Code': "ADM001",  intentionally left out
            # 'Type of Admission': "Emergency",
        }

        overview_df = pd.read_csv(self.OVERVIEW_CSV, dtype=str)
        model_dict = {}
        for _, row in overview_df.iterrows():
            row['features'] = row['features'].replace("'", "").replace("[", "").replace("]", "")
            features_set = set(row['features'].split(', '))
            model_dict[frozenset(features_set)] = row['model_path']

        present_features = list(broken_input.keys())
        model_features = frozenset(present_features)
        model_rel_path = model_dict.get(model_features)

        self.assertIsNone(model_rel_path, "There should be no model for this feature set")