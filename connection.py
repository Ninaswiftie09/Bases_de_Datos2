from neo4j import GraphDatabase

uri = "neo4j+s://a00b17cd.databases.neo4j.io"  
username = "neo4j"       
password = "eaeAtUZmYcjJ16jN2_uTQ4gIaOCq1GvbmFLlQYcfj1o"       

driver = GraphDatabase.driver(uri, auth=(username, password))

def close_driver():
    driver.close()

# Example to run a query
with driver.session() as session:
    result = session.run("MATCH (n) RETURN n LIMIT 5")
    for record in result:
        print(record)

close_driver()