# Modelo de Grafo - Sistema de Detección de Fraude

## 1. Descripción del caso de uso

Este sistema modela un entorno bancario enfocado en la **detección de fraude en transacciones**. Se representan usuarios, cuentas, transacciones, dispositivos y ubicaciones, junto con las relaciones entre ellas, para identificar patrones sospechosos como:

- Montos altos o inusuales
- Cadenas de transferencias entre cuentas
- Cuentas inactivas o recién creadas
- Ciclos de transacciones
- Dispositivos no confiables o compartidos
- Transacciones desde zonas de alto riesgo

El uso de un grafo permite detectar relaciones complejas entre entidades financieras que serían difíciles de identificar con bases de datos relacionales.

---

## 2. Diagrama del grafo

*(Diagrama exportado desde Neo4j Bloom — ver imagen adjunta del grafo)*

---

## 3. Labels (Nodos)

| Label        | Descripción                                              |
|--------------|----------------------------------------------------------|
| Usuario      | Persona que posee cuentas bancarias                      |
| Cuenta       | Cuenta bancaria asociada a uno o más usuarios            |
| Transaccion  | Movimiento de dinero entre cuentas                       |
| Dispositivo  | Dispositivo electrónico desde el cual se opera           |
| Ubicacion    | Localización geográfica de cuentas o transacciones       |

---

## 4. Propiedades por Label

### Usuario
| Propiedad           | Tipo    | Descripción                              |
|---------------------|---------|------------------------------------------|
| id_usuario          | String  | Identificador único del usuario          |
| nombre              | String  | Nombre completo del usuario              |
| edad                | Integer | Edad del usuario                         |
| fecha_registro      | Date    | Fecha de registro en el sistema          |
| verificado          | Boolean | Indica si el usuario está verificado     |
| correos_asociados   | List    | Lista de correos electrónicos asociados  |

### Cuenta
| Propiedad      | Tipo    | Descripción                                   |
|----------------|---------|-----------------------------------------------|
| id_cuenta      | String  | Identificador único de la cuenta              |
| saldo          | Float   | Saldo actual de la cuenta                     |
| tipo           | String  | Tipo de cuenta (ahorro, corriente, etc.)      |
| activa         | Boolean | Indica si la cuenta está activa               |
| fecha_creacion | Date    | Fecha de creación de la cuenta                |
| nivel_riesgo   | String  | Nivel de riesgo asignado (bajo, medio, alto)  |

### Transaccion
| Propiedad        | Tipo    | Descripción                                          |
|------------------|---------|------------------------------------------------------|
| id_transaccion   | String  | Identificador único de la transacción                |
| monto            | Float   | Monto de la transacción                              |
| fecha            | Date    | Fecha y hora de la transacción                       |
| tipo             | String  | Tipo de transacción (transferencia, pago, retiro...) |
| canal            | String  | Canal utilizado (app, web, cajero, sucursal)         |
| es_sospechosa    | Boolean | Indica si la transacción fue marcada como sospechosa |
| riesgo_score     | Float   | Puntuación de riesgo calculada (0.0 - 1.0)           |
| minuto_dia       | Integer | Minuto del día en que ocurrió (0-1439)               |
| etiquetas_alerta | List    | Lista de alertas asociadas a la transacción          |

### Dispositivo
| Propiedad        | Tipo    | Descripción                                      |
|------------------|---------|--------------------------------------------------|
| id_dispositivo   | String  | Identificador único del dispositivo              |
| tipo             | String  | Tipo de dispositivo (móvil, tablet, PC, etc.)    |
| ip               | String  | Dirección IP del dispositivo                     |
| sistema_operativo| String  | Sistema operativo del dispositivo                |
| confiable        | Boolean | Indica si el dispositivo es de confianza         |
| ultimo_uso       | Date    | Fecha del último uso registrado                  |

### Ubicacion
| Propiedad    | Tipo   | Descripción                                        |
|--------------|--------|----------------------------------------------------|
| id_ubicacion | String | Identificador único de la ubicación                |
| ciudad       | String | Ciudad de la ubicación                             |
| pais         | String | País de la ubicación                               |
| latitud      | Float  | Coordenada latitud                                 |
| longitud     | Float  | Coordenada longitud                                |
| zona_riesgo  | String | Clasificación de riesgo de la zona geográfica      |

---

## 5. Relaciones

| Relación        | Desde      | Hacia      | Descripción                                             |
|-----------------|------------|------------|---------------------------------------------------------|
| TIENE_CUENTA    | Usuario    | Cuenta     | Un usuario posee una o más cuentas bancarias            |
| RESIDE_EN       | Usuario    | Ubicacion  | Domicilio registrado del usuario                        |
| USA             | Usuario    | Dispositivo| Dispositivo desde el que el usuario opera               |
| EMITE           | Cuenta     | Transaccion| La cuenta origina una transacción (envío de dinero)     |
| TRANSFIERE_A    | Cuenta     | Cuenta     | Transferencia directa entre dos cuentas                 |
| REGISTRADA_EN   | Cuenta     | Ubicacion  | Ubicación física o de registro de la cuenta             |
| ASOCIADA_A      | Dispositivo| Cuenta     | Dispositivo vinculado a una cuenta para operar          |

---

## 6. Propiedades por Relación

### TIENE_CUENTA
| Propiedad      | Tipo    | Descripción                                         |
|----------------|---------|-----------------------------------------------------|
| fecha_creacion | Date    | Fecha en que el usuario adquirió la cuenta          |
| rol            | String  | Rol del usuario (titular, cotitular, autorizado)    |
| activa         | Boolean | Si la relación está activa                          |
| confianza      | Float   | Nivel de confianza de la relación (0.0 - 1.0)       |
| fuente         | String  | Fuente de la información (sistema, manual, csv)     |

### RESIDE_EN
| Propiedad      | Tipo    | Descripción                                          |
|----------------|---------|------------------------------------------------------|
| fecha_creacion | Date    | Fecha de registro del domicilio                      |
| tipo_domicilio | String  | Tipo (permanente, temporal, laboral)                 |
| confirmado     | Boolean | Si el domicilio ha sido verificado                   |
| confianza      | Float   | Nivel de confianza del dato                          |
| fuente         | String  | Fuente del registro                                  |

### USA
| Propiedad      | Tipo    | Descripción                                           |
|----------------|---------|-------------------------------------------------------|
| fecha_creacion | Date    | Primera vez que el usuario usó el dispositivo         |
| ultimo_uso     | Date    | Último acceso registrado                              |
| frecuencia_uso | Integer | Número de veces que se ha usado el dispositivo        |
| confianza      | Float   | Nivel de confianza de la relación                     |
| verificado     | Boolean | Si el dispositivo fue verificado por el usuario       |
| fuente         | String  | Fuente del registro                                   |

### EMITE
| Propiedad        | Tipo    | Descripción                                       |
|------------------|---------|---------------------------------------------------|
| fecha_creacion   | Date    | Fecha en que se registró la emisión               |
| monto_referencia | Float   | Monto de referencia de la transacción             |
| canal            | String  | Canal usado (app, web, cajero, sucursal)          |
| estado           | String  | Estado de la transacción (pendiente, completada)  |
| confianza        | Float   | Nivel de confianza de la relación                 |
| fuente           | String  | Fuente del registro                               |

### TRANSFIERE_A
| Propiedad       | Tipo    | Descripción                                        |
|-----------------|---------|----------------------------------------------------|
| fecha_creacion  | Date    | Fecha de la transferencia                          |
| canal           | String  | Canal de la transferencia                          |
| resultado       | String  | Resultado (exitosa, fallida, revertida)            |
| riesgo_relacion | Float   | Puntuación de riesgo de esta transferencia         |
| confianza       | Float   | Nivel de confianza de la relación                  |
| fuente          | String  | Fuente del registro                                |

### REGISTRADA_EN
| Propiedad      | Tipo    | Descripción                                         |
|----------------|---------|-----------------------------------------------------|
| fecha_creacion | Date    | Fecha de registro de la ubicación                   |
| sucursal       | String  | Nombre o código de la sucursal asociada             |
| verificada     | Boolean | Si la ubicación fue verificada formalmente          |
| confianza      | Float   | Nivel de confianza de la relación                   |
| fuente         | String  | Fuente del dato                                     |

### ASOCIADA_A
| Propiedad      | Tipo    | Descripción                                          |
|----------------|---------|------------------------------------------------------|
| fecha_creacion | Date    | Fecha en que el dispositivo fue asociado a la cuenta |
| primer_uso     | Date    | Primera vez que se usó el dispositivo en esa cuenta  |
| activo         | Boolean | Si la asociación está activa                         |
| confianza      | Float   | Nivel de confianza de la relación                    |
| fuente         | String  | Fuente del registro                                  |

---

## 7. Consideraciones del modelo

- El modelo garantiza un **grafo conexo**, donde todas las entidades están relacionadas entre sí a través de algún camino.
- Se utilizan todos los tipos de datos requeridos por la rúbrica:
  - **String** — nombres, IDs, estados, canales, tipos
  - **Integer** — edad, minuto_dia, frecuencia_uso
  - **Float** — saldo, monto, riesgo_score, latitud, longitud, confianza
  - **Boolean** — activa, verificado, confiable, es_sospechosa
  - **List** — correos_asociados, etiquetas_alerta
  - **Date** — fecha_registro, fecha_creacion, ultimo_uso, fecha
- El modelo supera el mínimo de **5000 nodos** generados y relacionados.
- La carga de datos se realiza mediante **archivos CSV** procesados en la aplicación.

---

## 8. Consultas Cypher relevantes

### 1. Cuentas con muchas transacciones en el mismo día.
```cypher
MATCH (c:Cuenta)-[:EMITE]->(t:Transaccion)
WHERE t.monto < 100
WITH c, t.fecha AS dia, count(t) AS cantidad, sum(t.monto) AS total
WHERE cantidad >= 8
RETURN c.id_cuenta, dia, cantidad, total
```

### 2. Dispositivos usados por más de un usuario.
```cypher
MATCH (u:Usuario)-[:USA]->(d:Dispositivo)
WITH d, collect(DISTINCT u.nombre) AS usuarios
WHERE size(usuarios) >= 2
RETURN d.id_dispositivo, size(usuarios), usuarios
```

### 3. Transacciones fuera del país o ciudad de residencia.
```cypher
MATCH (u:Usuario)-[:RESIDE_EN]->(ur:Ubicacion),
(u)-[:TIENE_CUENTA]->(c:Cuenta)-[:EMITE]->(t:Transaccion)-[:OCURRE_EN]->(ut:Ubicacion)
WHERE ur.pais <> ut.pais OR ur.ciudad <> ut.ciudad
RETURN u.nombre, c.id_cuenta, t.id_transaccion
```

### 4. Transacciones mayores a $10,000.
```cypher
MATCH (u:Usuario)-[:TIENE_CUENTA]->(c:Cuenta)-[:EMITE]->(t:Transaccion)
WHERE t.monto > 10000
RETURN u.nombre AS usuario, c.id_cuenta AS cuenta, t.id_transaccion AS transaccion, t.monto AS monto, t.fecha AS fecha
ORDER BY monto DESC
LIMIT $limit
```

### 5. Cuentas nuevas o inactivas con transferencias entrantes.
```cypher
MATCH (t:Transaccion)-[:TRANSFIERE_A]->(c:Cuenta)
WHERE c.activa = false OR c.fecha_creacion >= date('2026-03-01')
WITH c, count(t) AS recibidas, sum(t.monto) AS total
WHERE recibidas >= 3
RETURN c.id_cuenta AS cuenta, c.activa AS activa, c.fecha_creacion AS fecha_creacion, recibidas, round(total, 2) AS total
ORDER BY recibidas DESC
LIMIT $limit
```

### 6. Patrones de cuentas encadenadas por transferencias.
```cypher
MATCH path = (c1:Cuenta)-[:EMITE]->(:Transaccion)-[:TRANSFIERE_A]->(c2:Cuenta)<-[:TRANSFIERE_A]-(:Transaccion)<-[:EMITE]-(c3:Cuenta)
WHERE c1.id_cuenta <> c3.id_cuenta
RETURN c1.id_cuenta AS cuenta_origen, c2.id_cuenta AS cuenta_intermedia, c3.id_cuenta AS cuenta_relacionada, length(path) AS profundidad
LIMIT $limit
```

---

## 9. Conclusión

Este modelo de grafo permite representar de forma rica y expresiva las relaciones del sistema financiero, facilitando la detección de patrones fraudulentos mediante consultas Cypher sobre Neo4j. La estructura conexa del grafo, combinada con propiedades de riesgo en nodos y relaciones, permite implementar tanto consultas de filtrado simples como algoritmos avanzados de detección de anomalías y análisis de redes.
