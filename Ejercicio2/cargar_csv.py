import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg://nina:1234@localhost:5432/laboratorio4")

# cargar csv
df_costos = pd.read_csv("Ejercicio1/Datos_para_SQL/pais_poblacion.csv")
df_enve = pd.read_csv("Ejercicio1/Datos_para_SQL/pais_envejecimiento.csv")

# guardar en postgres
df_costos.to_sql("pais_costos", engine, if_exists="replace", index=False)
df_enve.to_sql("pais_envejecimiento", engine, if_exists="replace", index=False)

print("Datos cargados correctamente")