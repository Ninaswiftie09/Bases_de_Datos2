# Proyecto 02 - Neo4j

## Detección de fraude bancario

Este proyecto implementa una aplicación web para gestionar y consultar un modelo de grafos en Neo4j/AuraDB orientado a la detección de fraude en transacciones bancarias.

La solución está compuesta por:

- Backend en Python con FastAPI.
- Frontend en React con Vite.
- Base de datos Neo4j AuraDB.
- Carga masiva desde un CSV oficial publicado en GitHub Raw.
- Operaciones CRUD para nodos y relaciones.
- Consultas Cypher para detectar patrones sospechosos.
- Visualización básica del grafo.

## Modelo del grafo

El modelo utiliza las entidades presentadas en la propuesta del proyecto:

- Usuario
- Cuenta
- Transaccion
- Dispositivo
- Ubicacion

También se pueden crear nodos con más de una etiqueta desde la interfaz, por ejemplo:

```txt
Transaccion,Sospechosa
Usuario,Sospechoso
```

## Relaciones principales

El grafo maneja los siguientes tipos de relaciones:

```txt
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

Cada relación incluye propiedades como fecha, fuente, confianza, canal, estado o datos equivalentes según el tipo de relación.

## Requisitos

Para ejecutar el proyecto se requiere:

- Docker Desktop instalado.
- Docker Compose disponible.
- Una instancia activa de Neo4j AuraDB.
- Credenciales válidas de Neo4j.
- Acceso a internet para descargar el CSV oficial desde GitHub Raw.

## Configuración del backend

Dentro de la carpeta `backend`, cree un archivo `.env` con la siguiente estructura:

```env
NEO4J_URI=neo4j+s://SU_INSTANCIA.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=SU_PASSWORD
NEO4J_DATABASE=neo4j
FRONTEND_ORIGIN=http://localhost:3000
```

Si su instancia utiliza el ID de Aura como usuario, puede colocar ese valor en `NEO4J_USERNAME`. En Neo4j Aura, el valor de `NEO4J_DATABASE` normalmente debe ser `neo4j`.

No se recomienda guardar credenciales reales dentro del repositorio público.

## CSV oficial

La carga masiva se realiza desde el backend usando el siguiente enlace configurado en el código:

```txt
https://raw.githubusercontent.com/Ninaswiftie09/Bases_de_Datos2/refs/heads/Proyecto2/data/transacciones_fraude.csv
```

El frontend ya no solicita que el usuario pegue una URL. En la pantalla principal solo se muestra el botón para cargar el CSV oficial.

## Ejecución con Docker

Desde la raíz del proyecto, ejecute:

```bash
docker compose down --remove-orphans
docker compose up --build
```

Cuando los contenedores estén activos, use las siguientes rutas:

```txt
Frontend: http://localhost:3000
Backend:  http://localhost:8000
Docs API: http://localhost:8000/docs
```

## Flujo recomendado de uso

1. Abra el frontend en `http://localhost:3000`.
2. Ingrese a la pantalla `Inicio`.
3. Presione `Crear constraints`.
4. Presione `Cargar datos`.
5. Revise los conteos de nodos, relaciones y transacciones sospechosas.
6. Use las secciones `Nodos`, `Relaciones`, `Alertas` y `Grafo` para demostrar las funcionalidades.

## Funcionalidades principales

### Inicio

Permite ejecutar las acciones iniciales del sistema:

- Crear constraints.
- Cargar el CSV oficial.
- Limpiar la base de datos.
- Ver conteos por label y por tipo de relación.

### Nodos

Permite realizar operaciones CRUD sobre nodos:

- Crear nodos con una etiqueta.
- Crear nodos con dos o más etiquetas.
- Crear nodos con propiedades.
- Consultar nodos por label.
- Consultar nodos con filtros por propiedad.
- Actualizar propiedades de un nodo.
- Actualizar propiedades de varios nodos.
- Eliminar propiedades de un nodo.
- Eliminar propiedades de varios nodos.
- Eliminar un nodo.
- Eliminar varios nodos.

### Relaciones

Permite realizar operaciones CRUD sobre relaciones:

- Crear relaciones entre nodos existentes.
- Crear relaciones con propiedades.
- Consultar relaciones por tipo.
- Actualizar propiedades de una relación.
- Actualizar propiedades de varias relaciones.
- Eliminar propiedades de una relación.
- Eliminar propiedades de varias relaciones.
- Eliminar una relación.
- Eliminar varias relaciones.

### Alertas

Ejecuta consultas Cypher orientadas a patrones sospechosos:

- Microtransacciones frecuentes.
- Dispositivos compartidos por varios usuarios.
- Ubicaciones inusuales.
- Transacciones de monto alto.
- Cuentas nuevas o inactivas.
- Cadenas de transferencias.

También permite calcular un score de riesgo basado en reglas simples del modelo.

### Grafo

Muestra una visualización exploratoria de nodos y relaciones. Permite seleccionar un nodo y revisar sus propiedades principales.

## Endpoints relevantes

Algunos endpoints principales del backend son:

```txt
GET    /health
GET    /summary
POST   /setup/constraints
DELETE /setup/clear
POST   /load/default
POST   /nodes
GET    /nodes/{label}
PATCH  /nodes
DELETE /nodes
DELETE /nodes/properties
PATCH  /nodes/bulk
DELETE /nodes/bulk
POST   /relationships
GET    /relationships
PATCH  /relationships
DELETE /relationships
GET    /queries/{query_name}
GET    /fraud/score
GET    /graph/sample
```

## Pruebas rápidas desde consola

Verificar backend:

```bash
curl http://localhost:8000/health
```

Crear constraints:

```bash
curl -X POST http://localhost:8000/setup/constraints
```

Cargar CSV oficial:

```bash
curl -X POST "http://localhost:8000/load/default?batch_size=500&clear_before_load=false"
```

Consultar resumen:

```bash
curl http://localhost:8000/summary
```

## Estructura esperada del proyecto

```txt
Bases_de_Datos2/
├── backend/
│   ├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── package.json
│   └── index.html
├── data/
│   └── transacciones_fraude.csv
├── docs/
├── docker-compose.yml
└── README.md
```

