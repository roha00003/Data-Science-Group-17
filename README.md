# Data-Science-Group-17

*Predicting healthcare costs with explainable AI and machine learning*

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.0+-orange.svg)](https://scikit-learn.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-Latest-green.svg)](https://xgboost.readthedocs.io/)
[![Node](https://img.shields.io/badge/Node.js-latest-darkgreen.svg)](https://nodejs.org/)







## 📊 Overview

This project analyzes hospital cost drivers using machine learning and explainable AI techniques on New York State's SPARCS dataset (2022). We built predictive models to identify key factors influencing inpatient costs, length of stay, and mortality rates.

### 🎯 Key Objectives
- **Predict** total inpatient costs, length of stay, and mortality rates
- **Explore** cost optimization strategies through simulation

## 🔬 Dataset

**SPARCS (Statewide Planning and Research Cooperative System) 2022**
- 📈 2.2M+ inpatient discharge records → 724K after preprocessing
- 🏥 Comprehensive hospital data across New York State
- 📍 Geographic variables (hospital service areas, counties, ZIP codes)
- 👥 Patient demographics and clinical information

## 🤖 Machine Learning Models

### Models Used
- **Random Forest Regressor** - Ensemble learning with multiple decision trees
- **XGBoost Regressor** - Gradient boosting for optimized performance

### Multi-Output Prediction
Our models simultaneously predict:
1. **Total Costs** (R² ≈ 0.63)
2. **Length of Stay** (R² ≈ 0.68)
3. **Mortality Rate** (R² ≈ 0.23)

## 👥 Team

- **Aygün Çiloğlu** - s8aycilo@stud.uni-saarland.de
- **Robin Hans** - roha00003@stud.uni-saarland.de
- **Fabian Jost** 🙈 - s8fajost@stud.uni-saarland.de
- **Lukas Müller** - lumu00002@stud.uni-saarland.de
- **Sophie Orbán** - soor00001@stud.uni-saarland.de


## 🙏 Acknowledgments

We would like to thank Prof. Dr.-Ing. habil. oec. Wolfgang Maaß and the entire Data Science team for making this project possible.

---
## Running the Model
For running the programm or retraining the model, please look at the README.md in the Frontend and Backend folders 
