import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Leer el dataset
df = pd.read_csv("dataset_cardiovascular.csv")

# Variables de entrada
X = df[[
    "edad",
    "presion",
    "colesterol",
    "imc"
]]

# Variable objetivo
y = df["riesgo"]

# Dividir datos
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Entrenar modelo
modelo = RandomForestClassifier()

modelo.fit(X_train, y_train)

# Guardar modelo
joblib.dump(
    modelo,
    "modelos_entrenados/cardiovascular_model.pkl"
)

print("Modelo cardiovascular entrenado correctamente.")