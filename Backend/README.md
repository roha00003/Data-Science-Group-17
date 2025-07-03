# Data Science Group 17

## Prerequisites

- **Python**: Version 3.12 or higher (tested with 3.12.7)

## How to Start the Backend:
If you are not using a virtual environment skip to step 3:

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the server**:
   ```bash
   uvicorn src.backend_api:app --reload
   ```

## Data Placement
Ensure that the SPARCS data is in the data directory before retraining the model.

## Model Training
Model training is performed using the provided Jupyter Notebook. Open the notebook in your preferred environment to train and evaluate the models.
