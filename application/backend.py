import joblib
import pandas as pd

model=joblib.load(r"models/lgbm.joblib")

def create_df():
    df=pd.dataframe()
    return df.values

def predict(data):
    return None