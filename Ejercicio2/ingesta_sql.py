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

# 2.3 Integrar los datos en la memoria

df_integrado = df_costos.merge(
    df_envejecimiento,
    left_on="pais",
    right_on="nombre_pais",
    how="inner"
)

print("\nDatos integrados:")
print(df_integrado.head())

# 2.4 Cargar los datos integrados al Data Warehouse
from sqlalchemy import create_engine

engine_dw = create_engine(
    "postgresql+psycopg://nina:1234@localhost:5432/laboratorio4"
)

df_integrado.to_sql(
    "dw_paises",
    engine_dw,
    if_exists="replace",
    index=False
)

print("\nDatos cargados al Data Warehouse")