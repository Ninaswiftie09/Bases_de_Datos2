-- acá van todas las consultas SQL que se harán a la base de datos.

-- Ejercicio  1: Mostrar todo 
MATCH (n)-[r]-(m)
RETURN n, r, m

-- Ejercicio 2: Interacciones con Cypher

-- 2.1: Crear nodo nuevo con MERGE de Persona, con nombre "Michael Caine"

-- 2.2: Mostrar el nodo creado
MATCH (p:Person {name: 'Michael Caine'})
RETURN p

-- 2.3: Crear nodos nuevos con MERGE de Persona y Película
MERGE (p:Person {name: 'Katie Holmes'})
MERGE (m:Movie {title: 'The Dark Knight'})
RETURN p, m

-- 2.4: Cree una relación ACTED_IN para el actor Michael Caine y la película The Dark Night
MATCH (p:Person {name: 'Michael Caine'})
MATCH (m:Movie {title: 'The Dark Knight'})
MERGE (p)-[:ACTED_IN]->(m)
RETURN p, m

-- 2.5: Verifique que esa relación existe.
MATCH (p:Person {name: 'Michael Caine'})-[r:ACTED_IN]->(m:Movie {title: 'The Dark Knight'})
RETURN p, r, m

-- 2.6: utilice una cadena de comandos MERGE
-- para crear un nodo persona con el nombre Chadwick Boseman,
-- un nodo de tipo película con el título Black Panther y la relación ACTED_IN.
MERGE (p:Person {name: 'Chadwick Boseman'})
MERGE (m:Movie {title: 'Black Panther'})
MERGE (p)-[:ACTED_IN]->(m)
RETURN p, m

-- 2.7: Confirme que la relación haya funcionado.
MATCH (p:Person {name: 'Chadwick Boseman'})-[r:ACTED_IN]->(m:Movie {title: 'Black Panther'})
RETURN p, r, m

--2.8: Modifique el query para que en una misma consulta MERGE cree un nodo persona
-- (Emily Blunt), un nodo película (A Quiet Place) y la relación ACTED_IN.
MERGE (p:Person {name: 'Emily Blunt'})
MERGE (m:Movie {title: 'A Quiet Place'})
MERGE (p)-[:ACTED_IN]->(m)
RETURN p, m