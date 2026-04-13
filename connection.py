import os
import dotenv
from neo4j import GraphDatabase

load_status = dotenv.load_dotenv("Neo4j-a00b17cd-Created-2026-04-08.txt")
if load_status is False:
    raise RuntimeError("Environment variables not loaded.")

URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

if not URI or not AUTH[0] or not AUTH[1]:
    raise RuntimeError("Faltan variables de entorno de Neo4j.")


def get_driver():
    return GraphDatabase.driver(URI, auth=AUTH)


# funcion para probar la conexion
def probar_conexion():
    with get_driver() as driver:
        driver.verify_connectivity()
        print("Connection established.")


if __name__ == "__main__":
    probar_conexion()