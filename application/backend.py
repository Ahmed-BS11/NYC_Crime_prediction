import joblib
import pandas as pd

model=joblib.load("/models/lgbm.joblib")

def create_df():
    df=pd.dataframe()
    return df.values

def predict(data):
    return None