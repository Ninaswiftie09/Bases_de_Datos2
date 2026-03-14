import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

connection_url = URL.create(
    drivername="postgresql+psycopg",
    username="nina",
    password="1234",
    host="127.0.0.1",
    port=5433,
    database="laboratorio4",
)

print(connection_url)
engine = create_engine(connection_url)

df_costos = pd.read_sql("SELECT * FROM pais_costos;", engine)
df_envejecimiento = pd.read_sql("SELECT * FROM pais_envejecimiento;", engine)

print("Primeras filas de pais_costos:")
print(df_costos.head())
print()

print("Primeras filas de pais_envejecimiento:")
print(df_envejecimiento.head())
print()

print("Cantidad de registros en pais_costos:", len(df_costos))
print("Cantidad de registros en pais_envejecimiento:", len(df_envejecimiento))
print()

print("Nulos en pais_costos:")
print(df_costos.isnull().sum())
print()

print("Nulos en pais_envejecimiento:")
print(df_envejecimiento.isnull().sum())
print()