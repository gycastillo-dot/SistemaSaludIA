import pandas as pd
import random

datos = []

for i in range(1000):
    edad = random.randint(18, 80)
    glucosa = random.randint(70, 220)
    presion = random.randint(60, 140)
    imc = round(random.uniform(18, 40), 1)

    riesgo = 1 if (glucosa > 140 or imc > 30) else 0

    datos.append([edad, glucosa, presion, imc, riesgo])

df = pd.DataFrame(
    datos,
    columns=[
        "edad",
        "glucosa",
        "presion",
        "imc",
        "diabetes"
    ]
)

df.to_csv("dataset_diabetes.csv", index=False)

print("Dataset generado correctamente.")
