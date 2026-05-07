# Consultas para Neo4j Aura - Proyecto de Detección de Fraude

## 0. Consulta para limpiar datos demo antes de empezar


## 1. Consulta para crear constraints y evitar duplicados

Esta consulta ayuda a que Neo4j no cree usuarios, cuentas, transacciones, dispositivos o ubicaciones repetidas por ID.

```cypher
CREATE CONSTRAINT usuario_id IF NOT EXISTS
FOR (u:Usuario)
REQUIRE u.id_usuario IS UNIQUE;

CREATE CONSTRAINT cuenta_id IF NOT EXISTS
FOR (c:Cuenta)
REQUIRE c.id_cuenta IS UNIQUE;

CREATE CONSTRAINT transaccion_id IF NOT EXISTS
FOR (t:Transaccion)
REQUIRE t.id_transaccion IS UNIQUE;

CREATE CONSTRAINT dispositivo_id IF NOT EXISTS
FOR (d:Dispositivo)
REQUIRE d.id_dispositivo IS UNIQUE;

CREATE CONSTRAINT ubicacion_id IF NOT EXISTS
FOR (u:Ubicacion)
REQUIRE u.id_ubicacion IS UNIQUE;
```

---

## 2. Consulta para ver cuántos nodos hay por label

Sirve para demostrar que existen las 5 labels principales: `Usuario`, `Cuenta`, `Transaccion`, `Dispositivo` y `Ubicacion`.

```cypher
MATCH (n)
UNWIND labels(n) AS label
RETURN label, count(n) AS cantidad
ORDER BY cantidad DESC;
```

---

## 3. Consulta para ver cuántas relaciones hay por tipo

Sirve para demostrar que existen los 10 tipos de relaciones del modelo.

```cypher
MATCH ()-[r]->()
RETURN type(r) AS tipo_relacion, count(r) AS cantidad
ORDER BY tipo_relacion;
```

---

## 4. Consulta para ver resumen general de la base

Muestra total de nodos, total de relaciones y cantidad de transacciones marcadas como sospechosas.

```cypher
CALL {
  MATCH (n)
  RETURN count(n) AS total_nodos
}
CALL {
  MATCH ()-[r]->()
  RETURN count(r) AS total_relaciones
}
CALL {
  MATCH (t:Transaccion {es_sospechosa: true})
  RETURN count(t) AS transacciones_sospechosas
}
RETURN total_nodos, total_relaciones, transacciones_sospechosas;
```

---

## 5. Consulta para validar que hay mínimo 5000 nodos

La rúbrica pide mínimo 5000 nodos distintos.

```cypher
MATCH (n)
RETURN count(n) AS total_nodos,
       CASE WHEN count(n) >= 5000 THEN 'Cumple' ELSE 'No cumple' END AS estado;
```

---

## 6. Consulta para revisar si todos los nodos tienen al menos una relación

Esto ayuda a defender que el grafo no tiene nodos sueltos.

```cypher
MATCH (n)
WITH count(n) AS total_nodos
MATCH (m)
WHERE EXISTS { MATCH (m)--() }
RETURN total_nodos,
       count(m) AS nodos_conectados,
       total_nodos - count(m) AS nodos_aislados,
       CASE WHEN total_nodos = count(m) THEN 'Sin nodos aislados' ELSE 'Hay nodos aislados' END AS estado;
```

---

## 7. Consulta para revisar conectividad desde un nodo inicial

Esta consulta intenta ver cuántos nodos son alcanzables desde un nodo inicial. Si `nodos_alcanzables` es igual a `total_nodos`, el grafo se puede defender como conectado. Si la base está muy grande y tarda, bajá o subí la profundidad `0..12`.

```cypher
MATCH (inicio)
WITH inicio
LIMIT 1
MATCH (inicio)-[*0..12]-(alcanzable)
WITH count(DISTINCT alcanzable) AS nodos_alcanzables
MATCH (n)
RETURN nodos_alcanzables,
       count(n) AS total_nodos,
       CASE WHEN nodos_alcanzables = count(n) THEN 'Conexo en profundidad evaluada' ELSE 'Revisar profundidad o nodos aislados' END AS estado;
```

---

## 8. Consulta para crear un nodo con 1 label

Cubre CREATE de un nodo con una sola label.

```cypher
CREATE (u:Usuario:DemoCRUD {
  id_usuario: 'USU_DEMO_CRUD_001',
  nombre: 'Usuario Demo CRUD',
  edad: 25,
  verificado: true,
  correos_asociados: ['demo@correo.com', 'demo@banco.com'],
  fecha_registro: date('2026-05-01')
})
RETURN elementId(u) AS element_id, labels(u) AS labels, properties(u) AS propiedades;
```

---

## 9. Consulta para crear un nodo con 2 o más labels

Cubre CREATE de un nodo con múltiples labels.

```cypher
CREATE (u:Usuario:Sospechoso:DemoCRUD {
  id_usuario: 'USU_DEMO_CRUD_002',
  nombre: 'Usuario Demo Sospechoso',
  edad: 32,
  verificado: false,
  correos_asociados: ['sospechoso@correo.com'],
  fecha_registro: date('2026-05-02'),
  motivo_alerta: 'Prueba de múltiples labels'
})
RETURN elementId(u) AS element_id, labels(u) AS labels, properties(u) AS propiedades;
```

---

## 10. Consulta para crear nodos base de prueba

Estos nodos sirven para probar relaciones y CRUD sin tocar datos reales.

```cypher
MERGE (u:Usuario:DemoCRUD {id_usuario: 'USU_DEMO_CRUD_001'})
SET u.nombre = 'Usuario Demo CRUD',
    u.edad = 25,
    u.verificado = true,
    u.correos_asociados = ['demo@correo.com', 'demo@banco.com'],
    u.fecha_registro = date('2026-05-01')

MERGE (c:Cuenta:DemoCRUD {id_cuenta: 'CTA_DEMO_CRUD_001'})
SET c.saldo = 15000.50,
    c.tipo = 'ahorro',
    c.fecha_creacion = date('2026-04-15'),
    c.activa = true,
    c.nivel_riesgo = 'bajo'

MERGE (d:Dispositivo:DemoCRUD {id_dispositivo: 'DSP_DEMO_CRUD_001'})
SET d.tipo = 'movil',
    d.ip = '192.168.0.10',
    d.sistema_operativo = 'Android',
    d.confiable = false,
    d.ultimo_uso = date('2026-05-05')

MERGE (l:Ubicacion:DemoCRUD {id_ubicacion: 'UBI_DEMO_CRUD_001'})
SET l.pais = 'Guatemala',
    l.ciudad = 'Guatemala',
    l.latitud = 14.6349,
    l.longitud = -90.5069,
    l.zona_riesgo = false

RETURN u, c, d, l;
```

---

## 11. Consulta para consultar 1 nodo por ID del negocio

Ejemplo con `id_usuario`. Sirve para demostrar consulta de un solo nodo.

```cypher
MATCH (u:Usuario {id_usuario: 'USU_DEMO_CRUD_001'})
RETURN elementId(u) AS element_id, labels(u) AS labels, properties(u) AS propiedades;
```

---

## 12. Consulta para consultar 1 nodo por elementId

Copiá el `element_id` que te salga en otra consulta y pegalo aquí.

```cypher
MATCH (n)
WHERE elementId(n) = 'PEGA_AQUI_EL_ELEMENT_ID'
RETURN elementId(n) AS element_id, labels(n) AS labels, properties(n) AS propiedades;
```

---

## 13. Consulta para consultar muchos nodos con filtro

Ejemplo de búsqueda de muchos usuarios verificados.

```cypher
MATCH (u:Usuario)
WHERE u.verificado = true
RETURN elementId(u) AS element_id,
       u.id_usuario AS id_usuario,
       u.nombre AS nombre,
       u.edad AS edad,
       u.verificado AS verificado
LIMIT 25;
```

---

## 14. Consulta para consultar muchos nodos por label

Ejemplo para listar varias transacciones.

```cypher
MATCH (t:Transaccion)
RETURN elementId(t) AS element_id,
       t.id_transaccion AS id_transaccion,
       t.monto AS monto,
       t.fecha AS fecha,
       t.tipo AS tipo,
       t.canal AS canal,
       t.es_sospechosa AS es_sospechosa,
       t.riesgo_score AS riesgo_score
ORDER BY t.riesgo_score DESC
LIMIT 25;
```

---

## 15. Consulta para agregar una propiedad a 1 nodo

Cubre gestión de propiedades en un nodo.

```cypher
MATCH (u:Usuario {id_usuario: 'USU_DEMO_CRUD_001'})
SET u.revisado = true,
    u.comentario_revision = 'Propiedad agregada desde Aura'
RETURN u.id_usuario AS id_usuario, properties(u) AS propiedades;
```

---

## 16. Consulta para agregar propiedades a múltiples nodos

Cubre gestión de propiedades en múltiples nodos.

```cypher
MATCH (u:Usuario:DemoCRUD)
SET u.lote_revision = 'Lote demo CRUD',
    u.fecha_revision = date('2026-05-07')
RETURN count(u) AS nodos_actualizados;
```

---

## 17. Consulta para actualizar 1 propiedad de 1 nodo

Cubre UPDATE de un nodo.

```cypher
MATCH (u:Usuario {id_usuario: 'USU_DEMO_CRUD_001'})
SET u.edad = 26,
    u.verificado = false
RETURN u.id_usuario AS id_usuario, u.edad AS edad, u.verificado AS verificado;
```

---

## 18. Consulta para actualizar propiedades de múltiples nodos

Cubre UPDATE múltiple de nodos.

```cypher
MATCH (u:Usuario:DemoCRUD)
SET u.verificado = false,
    u.estado_revision = 'actualizado_en_lote'
RETURN count(u) AS nodos_actualizados;
```

---

## 19. Consulta para eliminar 1 o más propiedades de 1 nodo

Cubre eliminación de propiedades de un nodo.

```cypher
MATCH (u:Usuario {id_usuario: 'USU_DEMO_CRUD_001'})
REMOVE u.comentario_revision, u.revisado
RETURN u.id_usuario AS id_usuario, properties(u) AS propiedades;
```

---

## 20. Consulta para eliminar propiedades de múltiples nodos

Cubre eliminación de propiedades en varios nodos a la vez.

```cypher
MATCH (u:Usuario:DemoCRUD)
REMOVE u.lote_revision, u.fecha_revision, u.estado_revision
RETURN count(u) AS nodos_modificados;
```

---

## 21. Consulta para eliminar 1 nodo

Cubre DELETE de un nodo. Esta consulta crea primero un nodo temporal y luego lo elimina para no afectar datos reales.

```cypher
CREATE (x:TemporalDelete:DemoCRUD {id: 'TEMP_DELETE_001', creado_para: 'probar eliminacion de un nodo'})
WITH x
DETACH DELETE x
RETURN 'Nodo temporal eliminado correctamente' AS resultado;
```

---

## 22. Consulta para eliminar múltiples nodos

Cubre DELETE de varios nodos. Esta consulta crea nodos temporales y luego los elimina en lote.

```cypher
UNWIND range(1, 5) AS i
CREATE (:TemporalDelete:DemoCRUD {id: 'TEMP_BULK_DELETE_' + toString(i), creado_para: 'probar eliminacion multiple'})
WITH count(*) AS creados
MATCH (x:TemporalDelete:DemoCRUD)
WHERE x.id STARTS WITH 'TEMP_BULK_DELETE_'
WITH creados, collect(x) AS nodos
FOREACH (n IN nodos | DETACH DELETE n)
RETURN creados AS nodos_creados_y_eliminados;
```

---

## 23. Consulta para crear una relación con propiedades

Cubre CREATE de una relación entre dos nodos existentes con mínimo 3 propiedades.

```cypher
MATCH (u:Usuario:DemoCRUD {id_usuario: 'USU_DEMO_CRUD_001'})
MATCH (c:Cuenta:DemoCRUD {id_cuenta: 'CTA_DEMO_CRUD_001'})
MERGE (u)-[r:TIENE_CUENTA]->(c)
SET r.fecha_creacion = date('2026-05-07'),
    r.fuente = 'prueba_aura',
    r.confianza = 0.98,
    r.rol = 'titular',
    r.activa = true
RETURN elementId(r) AS element_id, type(r) AS tipo, properties(r) AS propiedades;
```

---

## 24. Consulta para crear varias relaciones demo

Esto ayuda a probar CRUD de relaciones y visualización del grafo.

```cypher
MATCH (u:Usuario:DemoCRUD {id_usuario: 'USU_DEMO_CRUD_001'})
MATCH (c:Cuenta:DemoCRUD {id_cuenta: 'CTA_DEMO_CRUD_001'})
MATCH (d:Dispositivo:DemoCRUD {id_dispositivo: 'DSP_DEMO_CRUD_001'})
MATCH (l:Ubicacion:DemoCRUD {id_ubicacion: 'UBI_DEMO_CRUD_001'})
MERGE (u)-[r1:TIENE_CUENTA]->(c)
SET r1.fecha_creacion = date('2026-05-07'), r1.fuente = 'prueba_aura', r1.confianza = 0.98, r1.rol = 'titular', r1.activa = true
MERGE (u)-[r2:USA]->(d)
SET r2.fecha_creacion = date('2026-05-07'), r2.fuente = 'prueba_aura', r2.confianza = 0.50, r2.frecuencia_uso = 1, r2.verificado = false
MERGE (u)-[r3:RESIDE_EN]->(l)
SET r3.fecha_creacion = date('2026-05-07'), r3.fuente = 'prueba_aura', r3.confianza = 0.90, r3.tipo_domicilio = 'principal', r3.confirmado = true
MERGE (d)-[r4:UBICADO_EN]->(l)
SET r4.fecha_creacion = date('2026-05-07'), r4.fuente = 'prueba_aura', r4.confianza = 0.85, r4.precision_gps = 25.0, r4.actualizado_en = date('2026-05-07')
RETURN r1, r2, r3, r4;
```

---

## 25. Consulta para consultar relaciones

Muestra relaciones con su `elementId`, tipo, nodo origen, nodo destino y propiedades.

```cypher
MATCH (a)-[r]->(b)
RETURN elementId(r) AS element_id,
       type(r) AS tipo_relacion,
       labels(a) AS labels_origen,
       properties(a) AS nodo_origen,
       labels(b) AS labels_destino,
       properties(b) AS nodo_destino,
       properties(r) AS propiedades_relacion
LIMIT 25;
```

---

## 26. Consulta para agregar propiedad a 1 relación

Cubre agregar propiedades a una relación específica.

```cypher
MATCH (:Usuario:DemoCRUD {id_usuario: 'USU_DEMO_CRUD_001'})-[r:USA]->(:Dispositivo:DemoCRUD {id_dispositivo: 'DSP_DEMO_CRUD_001'})
SET r.comentario = 'Relación revisada desde Aura',
    r.revisada = true
RETURN elementId(r) AS element_id, type(r) AS tipo, properties(r) AS propiedades;
```

---

## 27. Consulta para agregar propiedades a múltiples relaciones

Cubre agregar propiedades a varias relaciones a la vez.

```cypher
MATCH ()-[r:TIENE_CUENTA]->()
WHERE r.fuente = 'prueba_aura'
SET r.lote_revision = 'relaciones_demo',
    r.revisada_en = date('2026-05-07')
RETURN count(r) AS relaciones_actualizadas;
```

---

## 28. Consulta para actualizar 1 relación

Cubre UPDATE de una relación específica.

```cypher
MATCH (:Usuario:DemoCRUD {id_usuario: 'USU_DEMO_CRUD_001'})-[r:USA]->(:Dispositivo:DemoCRUD {id_dispositivo: 'DSP_DEMO_CRUD_001'})
SET r.confianza = 0.30,
    r.frecuencia_uso = 5
RETURN elementId(r) AS element_id, type(r) AS tipo, properties(r) AS propiedades;
```

---

## 29. Consulta para actualizar múltiples relaciones

Cubre UPDATE de varias relaciones al mismo tiempo.

```cypher
MATCH ()-[r]->()
WHERE r.fuente = 'prueba_aura'
SET r.estado_revision = 'actualizada_en_lote'
RETURN type(r) AS tipo_relacion, count(r) AS relaciones_actualizadas
ORDER BY tipo_relacion;
```

---

## 30. Consulta para eliminar propiedades de 1 relación

Cubre eliminación de propiedades de una relación.

```cypher
MATCH (:Usuario:DemoCRUD {id_usuario: 'USU_DEMO_CRUD_001'})-[r:USA]->(:Dispositivo:DemoCRUD {id_dispositivo: 'DSP_DEMO_CRUD_001'})
REMOVE r.comentario, r.revisada
RETURN elementId(r) AS element_id, type(r) AS tipo, properties(r) AS propiedades;
```

---

## 31. Consulta para eliminar propiedades de múltiples relaciones

Cubre eliminación de propiedades de varias relaciones al mismo tiempo.

```cypher
MATCH ()-[r]->()
WHERE r.fuente = 'prueba_aura'
REMOVE r.lote_revision, r.revisada_en, r.estado_revision
RETURN type(r) AS tipo_relacion, count(r) AS relaciones_modificadas
ORDER BY tipo_relacion;
```

---

## 32. Consulta para eliminar 1 relación

Cubre DELETE de una relación específica. Esta borra solo la relación demo `USA`.

```cypher
MATCH (:Usuario:DemoCRUD {id_usuario: 'USU_DEMO_CRUD_001'})-[r:USA]->(:Dispositivo:DemoCRUD {id_dispositivo: 'DSP_DEMO_CRUD_001'})
DELETE r
RETURN 'Relación USA demo eliminada' AS resultado;
```

---

## 33. Consulta para eliminar múltiples relaciones

Cubre DELETE de varias relaciones al mismo tiempo. Esta borra relaciones demo creadas con `fuente = 'prueba_aura'`.

```cypher
MATCH ()-[r]->()
WHERE r.fuente = 'prueba_aura'
WITH r, type(r) AS tipo
DELETE r
RETURN tipo, count(*) AS relaciones_eliminadas
ORDER BY tipo;
```

---

## 34. Consulta agregada para promedio de monto por tipo de transacción

Sirve para demostrar agregaciones dentro de nodos/transacciones.

```cypher
MATCH (t:Transaccion)
RETURN coalesce(t.tipo, 'Sin tipo') AS tipo_transaccion,
       round(avg(toFloat(t.monto)) * 100) / 100 AS promedio_monto,
       count(t) AS cantidad_transacciones
ORDER BY promedio_monto DESC;
```

---

## 35. Consulta agregada para transacciones sospechosas por ciudad

Sirve para demostrar agregaciones y relación entre `Transaccion` y `Ubicacion`.

```cypher
MATCH (t:Transaccion)-[:OCURRE_EN]->(u:Ubicacion)
WHERE coalesce(t.es_sospechosa, false) = true
RETURN coalesce(u.ciudad, 'Sin ciudad') AS ciudad,
       count(t) AS total_sospechosas
ORDER BY total_sospechosas DESC, ciudad ASC
LIMIT 25;
```

---

## 36. Consulta agregada para nivel de riesgo de cuentas

Sirve para ver cuántas cuentas hay por nivel de riesgo.

```cypher
MATCH (c:Cuenta)
RETURN coalesce(c.nivel_riesgo, 'Sin riesgo') AS nivel_riesgo,
       count(c) AS cantidad_cuentas,
       round(avg(toFloat(c.saldo)) * 100) / 100 AS saldo_promedio
ORDER BY cantidad_cuentas DESC;
```

---

## 37. Consulta agregada para dispositivos confiables vs no confiables

Sirve para demostrar uso de booleanos.

```cypher
MATCH (d:Dispositivo)
RETURN d.confiable AS dispositivo_confiable,
       count(d) AS cantidad
ORDER BY cantidad DESC;
```

---

## 38. Consulta para ver ejemplos de todos los tipos de datos usados

Demuestra string, float, integer, boolean, list y date.

```cypher
MATCH (t:Transaccion)
RETURN t.id_transaccion AS string_id,
       t.monto AS float_monto,
       t.minuto_dia AS integer_minuto,
       t.es_sospechosa AS boolean_sospechosa,
       t.etiquetas_alerta AS lista_alertas,
       t.fecha AS date_fecha
LIMIT 10;
```

---

## 39. Consulta funcional de fraude: microtransacciones frecuentes

Busca cuentas con muchas transacciones menores a 100.

```cypher
MATCH (c:Cuenta)-[:EMITE]->(t:Transaccion)
WHERE t.monto < 100
WITH c, t.fecha AS dia, count(t) AS cantidad, sum(t.monto) AS total, collect(t.id_transaccion)[0..10] AS transacciones
WHERE cantidad >= 8
RETURN c.id_cuenta AS cuenta,
       dia,
       cantidad,
       round(total * 100) / 100 AS total,
       transacciones
ORDER BY cantidad DESC
LIMIT 50;
```

---

## 40. Consulta funcional de fraude: dispositivos compartidos

Detecta dispositivos usados por más de un usuario.

```cypher
MATCH (u:Usuario)-[:USA]->(d:Dispositivo)
WITH d, collect(DISTINCT u.nombre) AS usuarios, collect(DISTINCT u.id_usuario) AS ids_usuarios
WHERE size(ids_usuarios) >= 2
RETURN d.id_dispositivo AS dispositivo,
       size(ids_usuarios) AS total_usuarios,
       usuarios[0..10] AS usuarios
ORDER BY total_usuarios DESC
LIMIT 50;
```

---

## 41. Consulta funcional de fraude: ubicaciones inusuales

Compara la ubicación de residencia del usuario con la ubicación de la transacción.

```cypher
MATCH (u:Usuario)-[:RESIDE_EN]->(ur:Ubicacion),
      (u)-[:TIENE_CUENTA]->(c:Cuenta)-[:EMITE]->(t:Transaccion)-[:OCURRE_EN]->(ut:Ubicacion)
WHERE ur.pais <> ut.pais OR ur.ciudad <> ut.ciudad
RETURN u.nombre AS usuario,
       c.id_cuenta AS cuenta,
       t.id_transaccion AS transaccion,
       ur.ciudad AS ciudad_residencia,
       ut.ciudad AS ciudad_transaccion,
       ut.pais AS pais_transaccion
LIMIT 50;
```

---

## 42. Consulta funcional de fraude: montos altos

Busca transacciones con monto mayor a 10000.

```cypher
MATCH (u:Usuario)-[:TIENE_CUENTA]->(c:Cuenta)-[:EMITE]->(t:Transaccion)
WHERE t.monto > 10000
RETURN u.nombre AS usuario,
       c.id_cuenta AS cuenta,
       t.id_transaccion AS transaccion,
       t.monto AS monto,
       t.fecha AS fecha
ORDER BY monto DESC
LIMIT 50;
```

---

## 43. Consulta funcional de fraude: cuentas nuevas o inactivas que reciben dinero

Busca cuentas destino inactivas o creadas recientemente que reciben varias transacciones.

```cypher
MATCH (t:Transaccion)-[:TRANSFIERE_A]->(c:Cuenta)
WHERE c.activa = false OR c.fecha_creacion >= date('2026-03-01')
WITH c, count(t) AS recibidas, sum(t.monto) AS total
WHERE recibidas >= 3
RETURN c.id_cuenta AS cuenta,
       c.activa AS activa,
       c.fecha_creacion AS fecha_creacion,
       recibidas,
       round(total * 100) / 100 AS total
ORDER BY recibidas DESC
LIMIT 50;
```

---

## 44. Consulta funcional de fraude: cadenas de transferencias

Busca cuentas relacionadas por caminos de transferencia.

```cypher
MATCH path = (c1:Cuenta)-[:EMITE]->(:Transaccion)-[:TRANSFIERE_A]->(c2:Cuenta)<-[:TRANSFIERE_A]-(:Transaccion)<-[:EMITE]-(c3:Cuenta)
WHERE c1.id_cuenta <> c3.id_cuenta
RETURN c1.id_cuenta AS cuenta_origen,
       c2.id_cuenta AS cuenta_intermedia,
       c3.id_cuenta AS cuenta_relacionada,
       length(path) AS profundidad
LIMIT 50;
```

---

## 45. Consulta funcional de fraude: score de riesgo por usuario y cuenta

Esta consulta funciona como scoring de riesgo usando reglas del sistema.

```cypher
MATCH (u:Usuario)-[:TIENE_CUENTA]->(c:Cuenta)
OPTIONAL MATCH (c)-[:EMITE]->(t_small:Transaccion)
WHERE t_small.monto < 100
WITH u, c, count(t_small) AS micro_count
OPTIONAL MATCH (u)-[:USA]->(d:Dispositivo)
WITH u, c, micro_count,
     count(DISTINCT CASE WHEN d.confiable = false THEN d END) AS dispositivos_no_confiables,
     count(DISTINCT d) AS total_dispositivos
OPTIONAL MATCH (other:Usuario)-[:USA]->(d2:Dispositivo)<-[:USA]-(u)
WHERE other.id_usuario <> u.id_usuario
WITH u, c, micro_count, dispositivos_no_confiables, total_dispositivos, count(DISTINCT d2) AS dispositivos_compartidos
OPTIONAL MATCH (c)-[:EMITE]->(:Transaccion)-[:TRANSFIERE_A]->(dest:Cuenta)
WHERE dest.activa = false OR dest.fecha_creacion >= date('2026-03-01')
WITH u, c, micro_count, dispositivos_no_confiables, total_dispositivos, dispositivos_compartidos, count(DISTINCT dest) AS cuentas_destino_riesgo
WITH u, c,
     (CASE WHEN micro_count >= 10 THEN 35 ELSE 0 END) +
     (CASE WHEN dispositivos_no_confiables > 0 THEN 20 ELSE 0 END) +
     (CASE WHEN dispositivos_compartidos > 0 THEN 20 ELSE 0 END) +
     (CASE WHEN cuentas_destino_riesgo >= 3 THEN 25 ELSE 0 END) AS score,
     micro_count, dispositivos_no_confiables, dispositivos_compartidos, cuentas_destino_riesgo
WHERE score > 0
RETURN u.id_usuario AS id_usuario,
       u.nombre AS usuario,
       c.id_cuenta AS cuenta,
       score,
       micro_count,
       dispositivos_no_confiables,
       dispositivos_compartidos,
       cuentas_destino_riesgo,
       CASE WHEN score >= 70 THEN 'alto' WHEN score >= 40 THEN 'medio' ELSE 'bajo' END AS nivel_riesgo
ORDER BY score DESC
LIMIT 50;
```

---

## 46. Consulta para visualizar un subgrafo en Neo4j Browser

Sirve para enseñar visualmente las conexiones entre usuario, cuenta, transacción, dispositivo y ubicación.

```cypher
MATCH path = (u:Usuario)-[*1..3]-(n)
RETURN path
LIMIT 50;
```

---

## 47. Consulta para visualizar transacciones sospechosas como grafo

Muestra relaciones alrededor de transacciones sospechosas.

```cypher
MATCH path = (c:Cuenta)-[:EMITE]->(t:Transaccion {es_sospechosa: true})-[:TRANSFIERE_A]->(destino:Cuenta)
RETURN path
LIMIT 50;
```

---

## 48. Consulta para ver el camino completo de una transacción

Muestra usuario, cuenta origen, transacción, cuenta destino, dispositivo y ubicación.

```cypher
MATCH (u:Usuario)-[:TIENE_CUENTA]->(origen:Cuenta)-[:EMITE]->(t:Transaccion)-[:TRANSFIERE_A]->(destino:Cuenta),
      (t)-[:SE_REALIZA_DESDE]->(d:Dispositivo),
      (t)-[:OCURRE_EN]->(l:Ubicacion)
RETURN u.nombre AS usuario,
       origen.id_cuenta AS cuenta_origen,
       t.id_transaccion AS transaccion,
       t.monto AS monto,
       destino.id_cuenta AS cuenta_destino,
       d.id_dispositivo AS dispositivo,
       d.confiable AS dispositivo_confiable,
       l.ciudad AS ciudad,
       l.pais AS pais
LIMIT 25;
```

---

## 49. Consulta para cargar datos desde CSV público

Reemplazá `URL_DEL_CSV_RAW` con la URL raw del CSV en GitHub. Por ejemplo, debe verse como una URL de `raw.githubusercontent.com`.

```cypher
LOAD CSV WITH HEADERS FROM 'URL_DEL_CSV_RAW' AS row

MERGE (u:Usuario {id_usuario: row.usuario_id})
SET u.nombre = row.usuario_nombre,
    u.edad = toInteger(row.usuario_edad),
    u.verificado = toBoolean(row.usuario_verificado),
    u.correos_asociados = split(row.usuario_correos_asociados, '|'),
    u.fecha_registro = date(row.usuario_fecha_registro)

MERGE (co:Cuenta {id_cuenta: row.cuenta_origen_id})
SET co.saldo = toFloat(row.cuenta_origen_saldo),
    co.tipo = row.cuenta_origen_tipo,
    co.fecha_creacion = date(row.cuenta_origen_fecha_creacion),
    co.activa = toBoolean(row.cuenta_origen_activa),
    co.nivel_riesgo = row.cuenta_origen_nivel_riesgo

MERGE (cd:Cuenta {id_cuenta: row.cuenta_destino_id})
SET cd.saldo = toFloat(row.cuenta_destino_saldo),
    cd.tipo = row.cuenta_destino_tipo,
    cd.fecha_creacion = date(row.cuenta_destino_fecha_creacion),
    cd.activa = toBoolean(row.cuenta_destino_activa),
    cd.nivel_riesgo = row.cuenta_destino_nivel_riesgo

MERGE (t:Transaccion {id_transaccion: row.transaccion_id})
SET t.monto = toFloat(row.transaccion_monto),
    t.fecha = date(row.transaccion_fecha),
    t.minuto_dia = toInteger(row.transaccion_minuto_dia),
    t.tipo = row.transaccion_tipo,
    t.canal = row.transaccion_canal,
    t.etiquetas_alerta = split(row.transaccion_etiquetas_alerta, '|'),
    t.es_sospechosa = toBoolean(row.transaccion_es_sospechosa),
    t.riesgo_score = toInteger(row.transaccion_riesgo_score)

MERGE (d:Dispositivo {id_dispositivo: row.dispositivo_id})
SET d.tipo = row.dispositivo_tipo,
    d.ip = row.dispositivo_ip,
    d.sistema_operativo = row.dispositivo_sistema_operativo,
    d.confiable = toBoolean(row.dispositivo_confiable),
    d.ultimo_uso = date(row.dispositivo_ultimo_uso)

MERGE (ur:Ubicacion {id_ubicacion: row.ubicacion_residencia_id})
SET ur.pais = row.ubicacion_residencia_pais,
    ur.ciudad = row.ubicacion_residencia_ciudad,
    ur.latitud = toFloat(row.ubicacion_residencia_latitud),
    ur.longitud = toFloat(row.ubicacion_residencia_longitud),
    ur.zona_riesgo = toBoolean(row.ubicacion_residencia_zona_riesgo)

MERGE (ut:Ubicacion {id_ubicacion: row.ubicacion_transaccion_id})
SET ut.pais = row.ubicacion_transaccion_pais,
    ut.ciudad = row.ubicacion_transaccion_ciudad,
    ut.latitud = toFloat(row.ubicacion_transaccion_latitud),
    ut.longitud = toFloat(row.ubicacion_transaccion_longitud),
    ut.zona_riesgo = toBoolean(row.ubicacion_transaccion_zona_riesgo)

MERGE (uc:Ubicacion {id_ubicacion: row.ubicacion_cuenta_id})
SET uc.pais = row.ubicacion_cuenta_pais,
    uc.ciudad = row.ubicacion_cuenta_ciudad,
    uc.latitud = toFloat(row.ubicacion_cuenta_latitud),
    uc.longitud = toFloat(row.ubicacion_cuenta_longitud),
    uc.zona_riesgo = toBoolean(row.ubicacion_cuenta_zona_riesgo)

MERGE (ud:Ubicacion {id_ubicacion: row.ubicacion_dispositivo_id})
SET ud.pais = row.ubicacion_dispositivo_pais,
    ud.ciudad = row.ubicacion_dispositivo_ciudad,
    ud.latitud = toFloat(row.ubicacion_dispositivo_latitud),
    ud.longitud = toFloat(row.ubicacion_dispositivo_longitud),
    ud.zona_riesgo = toBoolean(row.ubicacion_dispositivo_zona_riesgo)

MERGE (u)-[r1:TIENE_CUENTA]->(co)
SET r1.fecha_creacion = date(row.cuenta_origen_fecha_creacion),
    r1.fuente = 'csv',
    r1.confianza = 0.98,
    r1.rol = 'titular',
    r1.activa = toBoolean(row.cuenta_origen_activa)

MERGE (co)-[r2:EMITE]->(t)
SET r2.fecha_creacion = date(row.transaccion_fecha),
    r2.fuente = 'csv',
    r2.confianza = 0.97,
    r2.canal = row.transaccion_canal,
    r2.estado = 'procesada',
    r2.monto_referencia = toFloat(row.transaccion_monto)

MERGE (t)-[r3:TRANSFIERE_A]->(cd)
SET r3.fecha_creacion = date(row.transaccion_fecha),
    r3.fuente = 'csv',
    r3.confianza = 0.96,
    r3.canal = row.transaccion_canal,
    r3.resultado = 'aprobada',
    r3.riesgo_relacion = toInteger(row.transaccion_riesgo_score)

MERGE (u)-[r4:USA]->(d)
SET r4.fecha_creacion = date(row.usuario_fecha_registro),
    r4.fuente = 'csv',
    r4.confianza = CASE WHEN toBoolean(row.dispositivo_confiable) THEN 0.92 ELSE 0.45 END,
    r4.frecuencia_uso = 1,
    r4.verificado = toBoolean(row.dispositivo_confiable),
    r4.ultimo_uso = date(row.dispositivo_ultimo_uso)

MERGE (u)-[r5:RESIDE_EN]->(ur)
SET r5.fecha_creacion = date(row.usuario_fecha_registro),
    r5.fuente = 'csv',
    r5.confianza = 0.90,
    r5.tipo_domicilio = 'principal',
    r5.confirmado = true

MERGE (t)-[r6:SE_REALIZA_DESDE]->(d)
SET r6.fecha_creacion = date(row.transaccion_fecha),
    r6.fuente = 'csv',
    r6.confianza = CASE WHEN toBoolean(row.dispositivo_confiable) THEN 0.90 ELSE 0.40 END,
    r6.canal = row.transaccion_canal,
    r6.autenticacion = CASE WHEN toBoolean(row.dispositivo_confiable) THEN 'normal' ELSE 'debil' END,
    r6.riesgo = toInteger(row.transaccion_riesgo_score)

MERGE (t)-[r7:OCURRE_EN]->(ut)
SET r7.fecha_creacion = date(row.transaccion_fecha),
    r7.fuente = 'csv',
    r7.confianza = 0.88,
    r7.zona_horaria = 'America/Guatemala',
    r7.gps_confirmado = true,
    r7.tipo_evento = row.transaccion_tipo

MERGE (co)-[r8:REGISTRADA_EN]->(uc)
SET r8.fecha_creacion = date(row.cuenta_origen_fecha_creacion),
    r8.fuente = 'csv',
    r8.confianza = 0.94,
    r8.sucursal = row.ubicacion_cuenta_ciudad,
    r8.verificada = true

MERGE (co)-[r9:ASOCIADA_A]->(d)
SET r9.fecha_creacion = date(row.cuenta_origen_fecha_creacion),
    r9.fuente = 'csv',
    r9.confianza = CASE WHEN toBoolean(row.dispositivo_confiable) THEN 0.91 ELSE 0.50 END,
    r9.primer_uso = date(row.cuenta_origen_fecha_creacion),
    r9.activo = toBoolean(row.cuenta_origen_activa)

MERGE (d)-[r10:UBICADO_EN]->(ud)
SET r10.fecha_creacion = date(row.dispositivo_ultimo_uso),
    r10.fuente = 'csv',
    r10.confianza = 0.85,
    r10.precision_gps = 25.0,
    r10.actualizado_en = date(row.dispositivo_ultimo_uso);
```

---

## 50. Consulta para limpiar todos los datos demo al final


```cypher
MATCH (n:DemoCRUD)
DETACH DELETE n
RETURN 'Datos demo eliminados' AS resultado;
```

---

## 51. Consulta peligrosa para borrar toda la base


```cypher
MATCH (n)
DETACH DELETE n;
```
