import pandas as pd
import joblib
import os

from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv("dataset_diabetes.csv")

X = df[["edad","glucosa","presion","imc"]]
y = df["riesgo"]

modelo = RandomForestClassifier(n_estimators=100)

modelo.fit(X, y)

os.makedirs("modelos_entrenados", exist_ok=True)

joblib.dump(
    modelo,
    "modelos_entrenados/diabetes_model.pkl"
)

print("Modelo entrenado")