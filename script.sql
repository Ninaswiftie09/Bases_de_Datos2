-- acá van todas las consultas SQL que se harán a la base de datos.

-- Ejercicio  1: Mostrar todo 
MATCH (n)-[r]-(m)
RETURN n, r, m
