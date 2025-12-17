import pandas as pd
from scipy.stats import ks_2samp

baseline = pd.read_csv("feature_store.csv")
new_data = baseline.sample(frac=0.2)

for col in ["return", "ma5", "ma10", "volatility"]:
    stat, p = ks_2samp(baseline[col], new_data[col])
    if p < 0.05:
        print(f"⚠ Drift detected in {col}")
    else:
        print(f"✅ No drift in {col}")
