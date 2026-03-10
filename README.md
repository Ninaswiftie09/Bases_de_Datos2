# Proyecto 01 - MongoDB

Base inicial del proyecto con **MongoDB + mongo-express + Node.js/Express + Vue/Vite**vcon **Docker Compose**.

## Estructura del proyecto

```text
BASES_DE_DATOS2/
│
├── Backend/
├── Frontend/
├── .gitignore
├── docker-compose.yml
└── README.md
```

## Tecnologías usadas

- MongoDB 7
- mongo-express
- Node.js + Express
- Vue 3 + Vite
- Docker Compose

## Requisitos

Tener instalado:

- Docker
- Docker Compose

## Cómo levantar el proyecto

Desde la raíz del proyecto, donde está el archivo `docker-compose.yml`, ejecutar:

```bash
docker compose up --build
```

Si querés levantarlo en segundo plano:

```bash
docker compose up --build -d
```

## Servicios disponibles

Una vez levantados los contenedores, estos servicios deberían quedar disponibles:

- **Frontend:** `http://localhost:5173`
- **Backend:** `http://localhost:8000`
- **Health check del backend:** `http://localhost:8000/api/health`
- **Mongo Express:** `http://localhost:8081`
- **MongoDB:** `localhost:27017`

## Credenciales de MongoDB

Usuario administrador:

```text
admin
```

Contraseña:

```text
admin123
```

## URI de conexión a MongoDB

### Desde el contenedor del backend

```text
mongodb://admin:admin123@mongo:27017/?authSource=admin
```

### Desde la computadora con MongoDB Compass u otra herramienta

```text
mongodb://admin:admin123@localhost:27017/?authSource=admin
```

## Nombre de la base de datos

La base configurada actualmente es:

```text
proyecto01
```

## Cómo detener los contenedores

```bash
docker compose down
```

## Cómo detener y borrar volúmenes

```bash
docker compose down -v
```

> Esto elimina también la data almacenada en MongoDB.

## Comandos útiles

Ver contenedores corriendo:

```bash
docker ps
```

Ver logs:

```bash
docker compose logs -f
```

Ver logs solo del backend:

```bash
docker compose logs -f backend
```

Reconstruir servicios:

```bash
docker compose up --build
```
