// Modelo del grafo asumido:
// (:Cliente)-[:TIENE]->(:Cuenta)-[:REALIZO]->(:Transaccion)
//
// Nodos asumidos:
// Cliente {
//   nombre: texto,
//   tipo: texto
// }
//
// Cuenta {
//   numero: texto,
//   banco: texto
// }
//
// Transaccion {
//   id: texto,
//   monto: numero decimal,
//   fecha: fecha,
//   tipo: texto
// }
//
// Relaciones asumidas:
// (:Cliente)-[:TIENE]->(:Cuenta)
// (:Cuenta)-[:REALIZO]->(:Transaccion
// =======================================================
// 1. CARGA OPCIONAL DESDE CSV
// Crea los nodos Cliente, Cuenta y Transaccion.
// También crea las relaciones:
//
// Cliente -[:TIENE]-> Cuenta
// Cuenta -[:REALIZO]-> Transaccion
//
// Ejecutar esta parte SOLO si los nodos todavía no existen.
// El archivo transacciones.csv debe estar en la carpeta import de Neo4j.
// =======================================================

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/Ninaswiftie09/Bases_de_Datos2/refs/heads/Laboratorio8/transacciones.csv' AS row
MERGE (c:Cliente {nombre: row.cliente_nombre})
SET c.tipo = row.cliente_tipo
MERGE (cu:Cuenta {numero: row.cuenta_numero})
SET cu.banco = row.banco
MERGE (c)-[:TIENE]->(cu)
MERGE (t:Transaccion {id: row.tx_id})
SET t.monto = toFloat(row.tx_monto),
    t.fecha = date(row.tx_fecha),
    t.tipo = row.tx_tipo
MERGE (cu)-[:REALIZO]->(t);


// =======================================================
// 2. VERIFICACIÓN DE CARGA
// Estas queries sirven para comprobar que los datos sí existen.
// =======================================================

MATCH (c:Cliente)
RETURN count(c) AS total_clientes;

MATCH (cu:Cuenta)
RETURN count(cu) AS total_cuentas;

MATCH (t:Transaccion)
RETURN count(t) AS total_transacciones;


// =======================================================
// 3. VISUALIZACIÓN GENERAL DEL GRAFO
// Esta query se puede correr al inicio de la demo
// para mostrar cómo están conectados clientes, cuentas y transacciones.
// =======================================================

MATCH p = (c:Cliente)-[:TIENE]->(cu:Cuenta)-[:REALIZO]->(t:Transaccion)
RETURN p
LIMIT 50;


// =======================================================
// PISTA 1 - SUM()
// Caso: ¿Quién movió más dinero en total?
//
// Explicación:
// sum() suma todos los montos de las transacciones.
// En el caso de fraude, ayuda a identificar qué cliente
// acumuló el mayor movimiento de dinero.
// =======================================================

MATCH (c:Cliente)-[:TIENE]->(cu:Cuenta)-[:REALIZO]->(t:Transaccion)
RETURN c.nombre AS cliente,
       sum(t.monto) AS total_movido
ORDER BY total_movido DESC;


// =======================================================
// DISTRACTOR PARA PISTA 1
// Esta query usa avg(), pero no responde directamente
// quién movió más dinero en total.
// Sirve si en Menti gana una opción incorrecta.
// =======================================================

MATCH (c:Cliente)-[:TIENE]->(cu:Cuenta)-[:REALIZO]->(t:Transaccion)
RETURN c.nombre AS cliente,
       avg(t.monto) AS promedio_por_transaccion
ORDER BY promedio_por_transaccion DESC;


// =======================================================
// PISTA 2 - AVG()
// Caso: ¿Quién tiene el promedio de transacción más alto?
//
// Explicación:
// avg() calcula el promedio de los montos.
// Sirve para detectar clientes que tal vez no hicieron muchas
// transacciones, pero sí movieron montos altos en promedio.
// =======================================================

MATCH (c:Cliente)-[:TIENE]->(cu:Cuenta)-[:REALIZO]->(t:Transaccion)
RETURN c.nombre AS cliente,
       avg(t.monto) AS promedio_por_transaccion
ORDER BY promedio_por_transaccion DESC;


// =======================================================
// DISTRACTOR PARA PISTA 2
// Esta query usa sum(), pero no responde el promedio.
// Puede mostrar a alguien con mucho total, aunque sus transacciones
// individuales no sean tan altas.
// =======================================================

MATCH (c:Cliente)-[:TIENE]->(cu:Cuenta)-[:REALIZO]->(t:Transaccion)
RETURN c.nombre AS cliente,
       sum(t.monto) AS total_movido
ORDER BY total_movido DESC;


// =======================================================
// PISTA 3 - MAX()
// Caso: ¿Cuál fue la transacción más grande del caso?
//
// Explicación:
// max() encuentra el valor más alto.
// En el caso de fraude, ayuda a detectar el movimiento
// individual más extremo o sospechoso.
// =======================================================

MATCH (c:Cliente)-[:TIENE]->(cu:Cuenta)-[:REALIZO]->(t:Transaccion)
RETURN c.nombre AS cliente,
       max(t.monto) AS transaccion_mas_alta
ORDER BY transaccion_mas_alta DESC;


// =======================================================
// PISTA 4 - MIN()
// Caso: ¿Hay transacciones pequeñas sospechosas?
//
// Explicación:
// min() encuentra el valor más bajo.
// En fraude, puede servir para detectar microtransacciones
// o movimientos pequeños de prueba antes de un fraude mayor.
// =======================================================

MATCH (c:Cliente)-[:TIENE]->(cu:Cuenta)-[:REALIZO]->(t:Transaccion)
RETURN c.nombre AS cliente,
       min(t.monto) AS transaccion_mas_baja
ORDER BY transaccion_mas_baja ASC;


// =======================================================
// PISTA 5 - SUM() POR TIPO DE TRANSACCIÓN
// Caso: ¿Qué tipo de transacción movió más dinero?
//
// Explicación:
// Aquí se usa sum(), pero agrupando por tipo de transacción.
// Sirve para ver si el dinero sospechoso se concentra en
// transferencias, depósitos u otro tipo de movimiento.
// =======================================================

MATCH (t:Transaccion)
RETURN t.tipo AS tipo_transaccion,
       sum(t.monto) AS total_por_tipo
ORDER BY total_por_tipo DESC;


// =======================================================
// PISTA 6 - AVG() POR BANCO
// Caso: ¿En qué banco se mueven montos más altos en promedio?
//
// Explicación:
// Aquí se usa avg(), agrupando por banco.
// Sirve para comparar el comportamiento de las cuentas
// según el banco asociado.
// =======================================================

MATCH (cu:Cuenta)-[:REALIZO]->(t:Transaccion)
RETURN cu.banco AS banco,
       avg(t.monto) AS promedio_por_banco
ORDER BY promedio_por_banco DESC;


// =======================================================
// PISTA FINAL - QUERY COMBINADA
// Caso: ¿Quién es el principal sospechoso según el patrón completo?
//
// Explicación:
// Esta query combina sum(), avg(), min() y max().
// Una sola agregación puede dar una pista,
// pero juntas permiten comparar mejor el comportamiento.
// =======================================================

MATCH (c:Cliente)-[:TIENE]->(cu:Cuenta)-[:REALIZO]->(t:Transaccion)
RETURN c.nombre AS cliente,
       c.tipo AS tipo_cliente,
       sum(t.monto) AS total_movido,
       avg(t.monto) AS promedio_por_transaccion,
       min(t.monto) AS transaccion_mas_baja,
       max(t.monto) AS transaccion_mas_alta
ORDER BY total_movido DESC,
         promedio_por_transaccion DESC,
         transaccion_mas_alta DESC;


// =======================================================
// QUERY FINAL EXTRA - PERFIL COMPLETO POR CLIENTE Y BANCO
// Caso: ¿El patrón sospechoso se concentra en un banco específico?
//
// Explicación:
// Agrupa por cliente y banco. Ayuda a ver si el comportamiento
// sospechoso está asociado a una cuenta o banco concreto.
// =======================================================

MATCH (c:Cliente)-[:TIENE]->(cu:Cuenta)-[:REALIZO]->(t:Transaccion)
RETURN c.nombre AS cliente,
       cu.banco AS banco,
       count(t) AS cantidad_transacciones,
       sum(t.monto) AS total_movido,
       avg(t.monto) AS promedio_por_transaccion,
       min(t.monto) AS transaccion_mas_baja,
       max(t.monto) AS transaccion_mas_alta
ORDER BY total_movido DESC;


// =======================================================
// QUERY DE APOYO - TRANSACCIONES INDIVIDUALES MÁS ALTAS
// ayuda a mostrar
// cuáles fueron las transacciones más fuertes después
// de encontrar al sospechoso.
// =======================================================

MATCH (c:Cliente)-[:TIENE]->(cu:Cuenta)-[:REALIZO]->(t:Transaccion)
RETURN t.id AS transaccion,
       c.nombre AS cliente,
       cu.numero AS cuenta,
       cu.banco AS banco,
       t.tipo AS tipo,
       t.monto AS monto,
       t.fecha AS fecha
ORDER BY monto DESC
LIMIT 10;


// =======================================================
// QUERY DE APOYO - GRAFO DE UN SOSPECHOSO
// Sirve para mostrar visualmente sus cuentas y transacciones.
// =======================================================

MATCH p = (c:Cliente {nombre: 'Carlos Mendez'})-[:TIENE]->(cu:Cuenta)-[:REALIZO]->(t:Transaccion)
RETURN p;
