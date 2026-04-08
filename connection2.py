import os
import dotenv
from neo4j import GraphDatabase

load_status = dotenv.load_dotenv("Neo4j-a00b17cd-Created-2026-04-08.txt")
if load_status is False:
    raise RuntimeError('Environment variables not loaded.')


URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connection established.")