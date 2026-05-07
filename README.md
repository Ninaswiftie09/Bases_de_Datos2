# Proyecto 02 Neo4j - Detección de Fraude

Este proyecto implementa una aplicación web para gestionar y analizar un grafo de detección de fraude bancario usando Neo4j/AuraDB, un backend en Python con FastAPI y un frontend en React.

El sistema permite cargar datos desde CSV, crear nodos y relaciones, consultar información del grafo, actualizar propiedades, eliminar nodos o relaciones y ejecutar consultas Cypher orientadas a la detección de patrones sospechosos.

## 1. Estructura del proyecto

```text
fraude-neo4j/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── db.py
│   │   ├── graph_service.py
│   │   ├── schemas.py
│   │   ├── settings.py
│   │   └── utils.py
│   ├── scripts/
│   │   ├── constraints.cypher
│   │   └── load_csv.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── package.json
│   └── .env.example
├── data/
│   └── transacciones_fraude.csv
├── docs/
│   └── MODELO_GRAFO.md
└── README.md
```

## 2. Modelo del grafo

El modelo utiliza los nodos presentados en la propuesta del proyecto:

- `Usuario`
- `Cuenta`
- `Transaccion`
- `Dispositivo`
- `Ubicacion`

Cada label tiene más de cinco propiedades. El CSV también genera propiedades de diferentes tipos: texto, entero, decimal, booleano, lista y fecha.

### Relaciones implementadas

El sistema implementa las diez relaciones definidas en el diseño inicial:

```text
(Usuario)-[:TIENE_CUENTA]->(Cuenta)
(Cuenta)-[:EMITE]->(Transaccion)
(Transaccion)-[:TRANSFIERE_A]->(Cuenta)
(Usuario)-[:USA]->(Dispositivo)
(Usuario)-[:RESIDE_EN]->(Ubicacion)
(Transaccion)-[:SE_REALIZA_DESDE]->(Dispositivo)
(Transaccion)-[:OCURRE_EN]->(Ubicacion)
(Cuenta)-[:REGISTRADA_EN]->(Ubicacion)
(Cuenta)-[:ASOCIADA_A]->(Dispositivo)
(Dispositivo)-[:UBICADO_EN]->(Ubicacion)
```

Cada relación se crea con tres o más propiedades, por ejemplo: `fecha_creacion`, `fuente`, `confianza`, `canal`, `estado`, `riesgo`, entre otras.

## 3. Requisitos previos

Debe tener instalado lo siguiente:

- Python 3.11 o superior
- Node.js 18 o superior
- npm
- Una instancia activa de Neo4j AuraDB o Neo4j local

## 4. Configuración del backend

Ingrese a la carpeta del backend:

```bash
cd backend
```

Cree un entorno virtual:

```bash
python -m venv .venv
```

Active el entorno virtual.

En Windows PowerShell:

```bash
.venv\Scripts\activate
```

En Linux, macOS o Git Bash:

```bash
source .venv/bin/activate
```

Instale las dependencias:

```bash
pip install -r requirements.txt
```

Copie el archivo de variables de entorno:

```bash
cp .env.example .env
```

Edite el archivo `.env` y coloque sus credenciales de Neo4j/AuraDB:

```env
NEO4J_URI=neo4j+s://SU_INSTANCIA.databases.neo4j.io
NEO4J_USERNAME=SU_USUARIO
NEO4J_PASSWORD=SU_PASSWORD
NEO4J_DATABASE=SU_BASE_DE_DATOS
FRONTEND_ORIGIN=http://localhost:5173
```

Ejecute el backend:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La documentación automática del API estará disponible en:

```text
http://localhost:8000/docs
```

## 5. Configuración del frontend

En otra terminal, ingrese a la carpeta del frontend:

```bash
cd frontend
```

Instale las dependencias:

```bash
npm install
```

Copie el archivo de variables de entorno:

```bash
cp .env.example .env
```

Verifique que el archivo `.env` tenga la URL del backend:

```env
VITE_API_BASE=http://localhost:8000
```

Ejecute el frontend:

```bash
npm run dev
```

La aplicación estará disponible en:

```text
http://localhost:5173
```

## 6. Carga de datos

El proyecto incluye el archivo:

```text
data/transacciones_fraude.csv
```

Este archivo contiene 3200 transacciones y genera más de 5000 nodos distintos al cargarse en Neo4j.

### Opción A: cargar desde la interfaz

1. Abra el frontend en `http://localhost:5173`.
2. Ingrese al Dashboard.
3. Presione `Crear constraints`.
4. Presione `Cargar CSV local` si está ejecutando el backend desde la carpeta `backend`.
5. También puede subir el archivo CSV desde la opción de carga manual.
6. También puede pegar una URL raw del CSV si el archivo fue subido a GitHub.

### Opción B: cargar desde el endpoint

```bash
curl -X POST http://localhost:8000/load/local \
  -H "Content-Type: application/json" \
  -d '{"path":"../data/transacciones_fraude.csv", "batch_size":500, "clear_before_load":false}'
```

### Opción C: cargar desde script

Desde la carpeta `backend`:

```bash
python scripts/load_csv.py ../data/transacciones_fraude.csv
```

Para limpiar la base antes de cargar:

```bash
python scripts/load_csv.py ../data/transacciones_fraude.csv --clear
```

## 7. Funcionalidades principales

### Dashboard

Permite crear constraints, cargar CSV, limpiar la base de datos y revisar conteos por label y por tipo de relación.

### Nodos

Permite realizar operaciones CRUD sobre nodos:

- Crear nodo con una label.
- Crear nodo con dos o más labels.
- Crear nodo con cinco o más propiedades.
- Consultar nodos por label.
- Consultar nodos usando filtros.
- Agregar o actualizar propiedades de un nodo.
- Agregar o actualizar propiedades de múltiples nodos.
- Eliminar propiedades de un nodo.
- Eliminar propiedades de múltiples nodos.
- Eliminar un nodo.
- Eliminar múltiples nodos.

### Relaciones

Permite realizar operaciones CRUD sobre relaciones:

- Crear relación entre dos nodos existentes.
- Crear relación con tres o más propiedades.
- Consultar relaciones por tipo.
- Actualizar propiedades de una relación.
- Actualizar propiedades de múltiples relaciones.
- Eliminar propiedades de una relación.
- Eliminar propiedades de múltiples relaciones.
- Eliminar una relación.
- Eliminar múltiples relaciones.

### Consultas

Incluye consultas Cypher para detectar:

- Transacciones pequeñas y constantes.
- Dispositivos compartidos por varios usuarios.
- Transacciones desde ubicaciones inusuales.
- Transacciones de monto alto.
- Transferencias hacia cuentas nuevas o inactivas.
- Cadenas de transferencias entre cuentas relacionadas.

También incluye un score de riesgo como algoritmo simple de Data Science.

### Grafo

Muestra una visualización interactiva del grafo usando React. Permite observar nodos y relaciones de manera visual.

## 8. Consultas Cypher principales

### Transacciones pequeñas y constantes

```cypher
MATCH (c:Cuenta)-[:EMITE]->(t:Transaccion)
WHERE t.monto < 100
WITH c, t.fecha AS dia, count(t) AS cantidad, sum(t.monto) AS total, collect(t.id_transaccion)[0..10] AS transacciones
WHERE cantidad >= 8
RETURN c.id_cuenta AS cuenta, dia, cantidad, round(total, 2) AS total, transacciones
ORDER BY cantidad DESC;
```

### Dispositivos compartidos

```cypher
MATCH (u:Usuario)-[:USA]->(d:Dispositivo)
WITH d, collect(DISTINCT u.nombre) AS usuarios
WHERE size(usuarios) >= 2
RETURN d.id_dispositivo AS dispositivo, size(usuarios) AS total_usuarios, usuarios[0..10] AS usuarios
ORDER BY total_usuarios DESC;
```

### Ubicaciones inusuales

```cypher
MATCH (u:Usuario)-[:RESIDE_EN]->(ur:Ubicacion),
      (u)-[:TIENE_CUENTA]->(c:Cuenta)-[:EMITE]->(t:Transaccion)-[:OCURRE_EN]->(ut:Ubicacion)
WHERE ur.pais <> ut.pais OR ur.ciudad <> ut.ciudad
RETURN u.nombre AS usuario, c.id_cuenta AS cuenta, t.id_transaccion AS transaccion,
       ur.ciudad AS ciudad_residencia, ut.ciudad AS ciudad_transaccion, ut.pais AS pais_transaccion;
```

### Cuentas nuevas o inactivas

```cypher
MATCH (t:Transaccion)-[:TRANSFIERE_A]->(c:Cuenta)
WHERE c.activa = false OR c.fecha_creacion >= date('2026-03-01')
WITH c, count(t) AS recibidas, sum(t.monto) AS total
WHERE recibidas >= 3
RETURN c.id_cuenta AS cuenta, c.activa AS activa, c.fecha_creacion AS fecha_creacion, recibidas, round(total, 2) AS total
ORDER BY recibidas DESC;
```

## 9. Score de riesgo

El score de riesgo se calcula en el backend con base en estas señales:

- Muchas transacciones pequeñas desde una cuenta.
- Uso de dispositivos no confiables.
- Uso de dispositivos compartidos por varios usuarios.
- Transferencias hacia cuentas nuevas o inactivas.

La clasificación general es:

```text
0 - 39: riesgo bajo
40 - 69: riesgo medio
70 - 100: riesgo alto
```

## 10. Endpoints principales

```text
GET    /health
POST   /setup/constraints
DELETE /setup/clear
GET    /summary
POST   /load/local
POST   /load/url
POST   /load/upload
POST   /nodes
GET    /nodes/{label}
PATCH  /nodes
DELETE /nodes/properties
DELETE /nodes
PATCH  /nodes/bulk
DELETE /nodes/bulk/properties
DELETE /nodes/bulk
POST   /relationships
GET    /relationships
PATCH  /relationships
DELETE /relationships/properties
DELETE /relationships
PATCH  /relationships/bulk
DELETE /relationships/bulk/properties
DELETE /relationships/bulk
GET    /queries/{query_name}
GET    /fraud/score
GET    /graph/sample
```

## 11. Cobertura de rúbrica

El proyecto cubre los siguientes puntos:

- Caso de uso de detección de fraude.
- Mínimo cinco labels de nodos.
- Mínimo cinco propiedades por label.
- Mínimo diez tipos de relaciones.
- Mínimo tres propiedades por tipo de relación.
- Tipos de datos: string, float, integer, boolean, list y date.
- Carga masiva desde CSV.
- Más de 5000 nodos generados.
- Datos previamente cargables en Neo4j.
- Grafo conectado mediante usuarios, cuentas, transacciones, dispositivos y ubicaciones.
- CRUD de nodos.
- CRUD de relaciones.
- Consultas Cypher de fraude.
- Algoritmo de score de riesgo.
- Interfaz gráfica en React.

## 12. Recomendaciones para la presentación

Durante la presentación se recomienda seguir este orden:

1. Explicar el caso de uso de detección de fraude.
2. Mostrar el modelo de nodos y relaciones.
3. Mostrar la carga del CSV y el conteo de nodos.
4. Mostrar CRUD de nodos.
5. Mostrar CRUD de relaciones.
6. Mostrar consultas Cypher.
7. Mostrar el score de riesgo.
8. Mostrar la visualización del grafo.
9. Explicar cómo el sistema detecta transacciones pequeñas y constantes.

## 13. Notas de seguridad

No se recomienda subir el archivo `.env` al repositorio. Solamente debe subirse `.env.example`.

Las credenciales reales de Neo4j/AuraDB deben mantenerse fuera del repositorio público.
