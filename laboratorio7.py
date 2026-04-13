from connection import get_driver


# funcion para crear una persona
def crear_persona(tx, name, born):
    tx.run(
        """
        MERGE (p:Person {name: $name})
        SET p.born = $born
        """,
        name=name,
        born=born
    )


# funcion para crear una pelicula
def crear_pelicula(tx, title, released, tagline):
    tx.run(
        """
        MERGE (m:Movie {title: $title})
        SET m.released = $released,
            m.tagline = $tagline
        """,
        title=title,
        released=released,
        tagline=tagline
    )


# funcion para crear una relacion reviewd
def crear_review(tx, person_name, movie_title, rating, summary):
    tx.run(
        """
        MATCH (p:Person {name: $person_name})
        MATCH (m:Movie {title: $movie_title})
        MERGE (p)-[r:REVIEWED]->(m)
        SET r.rating = $rating,
            r.summary = $summary
        """,
        person_name=person_name,
        movie_title=movie_title,
        rating=rating,
        summary=summary
    )


# funcion para insertar datos
def llenar_datos(session):
    personas = [
        {"name": "Lab User 1", "born": 2003},
        {"name": "Lab User 2", "born": 2004},
        {"name": "Lab User 3", "born": 2002},
    ]

    peliculas = [
        {"title": "Lab Movie 1", "released": 2024, "tagline": "Movie created for the lab"},
        {"title": "Lab Movie 2", "released": 2023, "tagline": "Second movie created for the lab"},
        {"title": "Lab Movie 3", "released": 2022, "tagline": "Third movie created for the lab"},
        {"title": "Lab Movie 4", "released": 2021, "tagline": "Fourth movie created for the lab"},
    ]

    reviews = [
        {"person_name": "Lab User 1", "movie_title": "Lab Movie 1", "rating": 5, "summary": "Muy buena pelicula."},
        {"person_name": "Lab User 1", "movie_title": "Lab Movie 2", "rating": 4, "summary": "Me gusto bastante."},
        {"person_name": "Lab User 2", "movie_title": "Lab Movie 2", "rating": 5, "summary": "La recomendaria."},
        {"person_name": "Lab User 2", "movie_title": "Lab Movie 3", "rating": 3, "summary": "Esta bien, pero pudo ser mejor."},
        {"person_name": "Lab User 3", "movie_title": "Lab Movie 1", "rating": 4, "summary": "Buena historia."},
        {"person_name": "Lab User 3", "movie_title": "Lab Movie 4", "rating": 5, "summary": "Fue la que mas me gusto."},
    ]

    for persona in personas:
        session.execute_write(crear_persona, **persona)

    for pelicula in peliculas:
        session.execute_write(crear_pelicula, **pelicula)

    for review in reviews:
        session.execute_write(crear_review, **review)


# funcion para mostrar resultados
def mostrar_reviews(session):
    result = session.run(
        """
        MATCH (p:Person)-[r:REVIEWED]->(m:Movie)
        WHERE p.name STARTS WITH 'Lab User'
        RETURN p.name AS persona, m.title AS pelicula, r.rating AS rating, r.summary AS resumen
        ORDER BY persona, pelicula
        """
    )

    print("\nDatos insertados:\n")
    for record in result:
        print(
            f"{record['persona']} -> {record['pelicula']} | "
            f"rating: {record['rating']} | "
            f"summary: {record['resumen']}"
        )


# funcion principal
def main():
    with get_driver() as driver:
        driver.verify_connectivity()
        print("Connection established.")

        with driver.session() as session:
            llenar_datos(session)
            mostrar_reviews(session)


if __name__ == "__main__":
    main()