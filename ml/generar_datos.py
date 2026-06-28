import pandas as pd
import random

datos = []

for i in range(1000):

    edad = random.randint(18, 80)
    glucosa = random.randint(70, 250)
    presion = random.randint(60, 180)
    imc = round(random.uniform(18, 40), 1)

    riesgo = 0

    if glucosa > 140:
        riesgo = 1

    datos.append([
        edad,
        glucosa,
        presion,
        imc,
        riesgo
    ])

df = pd.DataFrame(
    datos,
    columns=[
        "edad",
        "glucosa",
        "presion",
        "imc",
        "riesgo"
    ]
)

df.to_csv(
    "dataset_diabetes.csv",
    index=False
)

print("Dataset generado")