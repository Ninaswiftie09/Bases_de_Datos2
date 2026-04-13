from connection import get_driver
import time


def crear_usuario(tx, name, user_id):
    tx.run(
        """
        MERGE (u:User {userId: $user_id})
        SET u.name = $name
        """,
        name=name,
        user_id=user_id
    )


def crear_pelicula(tx, title, movie_id, year, plot):
    tx.run(
        """
        MERGE (m:Movie {movieId: $movie_id})
        SET m.title  = $title,
            m.year   = $year,
            m.plot   = $plot
        """,
        title=title,
        movie_id=movie_id,
        year=year,
        plot=plot
    )


def crear_rated(tx, user_id, movie_id, rating, timestamp):
    tx.run(
        """
        MATCH (u:User  {userId:  $user_id})
        MATCH (m:Movie {movieId: $movie_id})
        MERGE (u)-[r:RATED]->(m)
        SET r.rating    = $rating,
            r.timestamp = $timestamp
        """,
        user_id=user_id,
        movie_id=movie_id,
        rating=rating,
        timestamp=timestamp
    )


def llenar_datos(session):
    usuarios = [
        {"name": "Alice García",   "user_id": "U001"},
        {"name": "Bob Martínez",   "user_id": "U002"},
        {"name": "Carlos López",   "user_id": "U003"},
        {"name": "Diana Pérez",    "user_id": "U004"},
        {"name": "Eduardo Ramírez","user_id": "U005"},
    ]

    peliculas = [
        {"title": "Inception",       "movie_id": 1, "year": 2010, "plot": "A thief who steals corporate secrets through dream-sharing technology."},
        {"title": "The Matrix",      "movie_id": 2, "year": 1999, "plot": "A hacker discovers the world is a simulation."},
        {"title": "Interstellar",    "movie_id": 3, "year": 2014, "plot": "Astronauts travel through a wormhole near Saturn."},
        {"title": "The Dark Knight", "movie_id": 4, "year": 2008, "plot": "Batman faces the Joker in Gotham City."},
        {"title": "Parasite",        "movie_id": 5, "year": 2019, "plot": "A poor family schemes to become employed by a wealthy family."},
    ]

    # Cada usuario califica al menos 2 películas
    rated = [
        {"user_id": "U001", "movie_id": 1, "rating": 5, "timestamp": int(time.time()) - 500},
        {"user_id": "U001", "movie_id": 3, "rating": 4, "timestamp": int(time.time()) - 400},
        {"user_id": "U002", "movie_id": 2, "rating": 5, "timestamp": int(time.time()) - 300},
        {"user_id": "U002", "movie_id": 4, "rating": 3, "timestamp": int(time.time()) - 200},
        {"user_id": "U003", "movie_id": 1, "rating": 4, "timestamp": int(time.time()) - 150},
        {"user_id": "U003", "movie_id": 5, "rating": 5, "timestamp": int(time.time()) - 100},
        {"user_id": "U004", "movie_id": 2, "rating": 3, "timestamp": int(time.time()) - 90},
        {"user_id": "U004", "movie_id": 3, "rating": 5, "timestamp": int(time.time()) - 80},
        {"user_id": "U005", "movie_id": 4, "rating": 4, "timestamp": int(time.time()) - 70},
        {"user_id": "U005", "movie_id": 5, "rating": 5, "timestamp": int(time.time()) - 60},
    ]

    for u in usuarios:
        session.execute_write(crear_usuario, **u)

    for p in peliculas:
        session.execute_write(crear_pelicula, **p)

    for r in rated:
        session.execute_write(crear_rated, **r)

    print("Datos insertados correctamente.")


def buscar_usuario(session, user_id):
    """Busca y retorna un usuario por su userId."""
    result = session.run(
        """
        MATCH (u:User {userId: $user_id})
        RETURN u.name AS nombre, u.userId AS id
        """,
        user_id=user_id
    )
    record = result.single()
    if record:
        print(f"\nUsuario encontrado -> nombre: {record['nombre']} | id: {record['id']}")
    else:
        print(f"\nNo se encontro el usuario con id: {user_id}")
    return record


def buscar_pelicula(session, movie_id):
    """Busca y retorna una película por su movieId."""
    result = session.run(
        """
        MATCH (m:Movie {movieId: $movie_id})
        RETURN m.title AS titulo, m.year AS año, m.plot AS sinopsis
        """,
        movie_id=movie_id
    )
    record = result.single()
    if record:
        print(f"\nPelicula encontrada -> titulo: {record['titulo']} | año: {record['año']}")
        print(f"   Sinopsis: {record['sinopsis']}")
    else:
        print(f"\nNo se encontro la pelicula con id: {movie_id}")
    return record


def buscar_usuario_con_ratings(session, user_id):
    """Busca un usuario junto con todas sus relaciones RATED hacia películas."""
    result = session.run(
        """
        MATCH (u:User {userId: $user_id})-[r:RATED]->(m:Movie)
        RETURN u.name AS usuario, m.title AS pelicula,
               r.rating AS rating, r.timestamp AS timestamp
        ORDER BY r.rating DESC
        """,
        user_id=user_id
    )
    records = result.data()
    if records:
        print(f"\nRatings del usuario '{records[0]['usuario']}':")
        for rec in records:
            print(f"   -> {rec['pelicula']} | rating: {rec['rating']} | timestamp: {rec['timestamp']}")
    else:
        print(f"\nNo se encontraron ratings para el usuario: {user_id}")
    return records


def mostrar_todos_los_ratings(session):
    result = session.run(
        """
        MATCH (u:User)-[r:RATED]->(m:Movie)
        RETURN u.name AS usuario, m.title AS pelicula,
               r.rating AS rating, r.timestamp AS timestamp
        ORDER BY usuario, pelicula
        """
    )
    print("\nTodos los ratings en el grafo:\n")
    for record in result:
        print(
            f"  {record['usuario']} → {record['pelicula']} | "
            f"rating: {record['rating']} | timestamp: {record['timestamp']}"
        )


def main():
    with get_driver() as driver:
        driver.verify_connectivity()
        print("Conexion establecida.")

        with driver.session() as session:

            # Inciso 2
            llenar_datos(session)
            mostrar_todos_los_ratings(session)

            # Inciso 3
            print("\n" + "="*55)
            print("INCISO 3 - Funciones de busqueda")
            print("="*55)

            buscar_usuario(session, "U001")
            buscar_pelicula(session, 2)
            buscar_usuario_con_ratings(session, "U003")


if __name__ == "__main__":
    main()