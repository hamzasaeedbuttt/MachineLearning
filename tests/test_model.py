import joblib

def test_model_loads():
    model = joblib.load("model_registry/random_forest_v1.joblib")
    assert model is not None
