# Datasets for Training the Lab Report Classifier

Place your downloaded CSV datasets in this folder. The ML training pipeline will look here for training data.

## Required Datasets

Download these from Kaggle (free account required) and place the CSV files in this folder:

### 1. Blood Values Dataset (RECOMMENDED — Start here)
- **Link**: https://www.kaggle.com/datasets/yakhyoakbarov/blood-values-new-dataset
- **Size**: 4,598 entries, 14 columns
- **Contains**: Glucose (fasting), Creatinine, Cholesterol, HDL, LDL, AST, ALT, BUN, and demographic info
- **Why**: Best general-purpose blood test dataset with multiple biomarkers

### 2. Diagnostic Pathology Test Results
- **Link**: https://www.kaggle.com/datasets/pareshbadnore/diagnostic-pathology-test-results
- **Contains**: Blood glucose, HbA1C, blood pressure, cholesterol, hemoglobin + condition labels (Fit, Anemia, Hypertension, Diabetes, High Cholesterol)
- **Why**: Already labeled with health conditions — ideal for training a condition classifier

### 3. Health Test by Blood Dataset
- **Link**: https://www.kaggle.com/datasets/simaanjali/health-test-by-blood-dataset
- **Contains**: Cholesterol, Triglycerides, HDL, LDL, Creatinine, BUN + cardiovascular risk data
- **Why**: Good for kidney and cardiovascular pattern detection

### 4. General Blood Dataset
- **Link**: https://www.kaggle.com/datasets/goktugdemirel/blood-dataset
- **Contains**: Blood chemistry (glucose, cholesterol, electrolytes), blood cell counts, hemoglobin
- **Why**: Broad coverage of common lab tests

## How the Training Works

Once you place the CSVs here, the training script (`app/ml/train_model.py`) will:
1. Load and merge the datasets
2. Normalize column names to match our reference range database
3. Engineer features (how far each value is from normal range, ratios between related markers)
4. Train a `RandomForestClassifier` to predict health conditions/risk patterns
5. Save the trained model to `app/ml/models/classifier_model.joblib`

## File Structure After Download

```
datasets/
├── README.md              (this file)
├── blood_values.csv       (from Dataset #1)
├── diagnostic_pathology.csv (from Dataset #2)
├── health_test_blood.csv  (from Dataset #3)
└── blood_dataset.csv      (from Dataset #4)
```

> **Note**: You only need Dataset #1 and #2 at minimum. Datasets #3 and #4 are optional for broader coverage.
