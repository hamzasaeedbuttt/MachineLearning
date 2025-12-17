import pandas as pd

def test_no_nulls():
    df = pd.read_csv("feature_store.csv")
    assert df.isnull().sum().sum() == 0
