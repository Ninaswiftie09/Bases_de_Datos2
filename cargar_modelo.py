import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

LADOS_BASICOS = ["arriba", "abajo", "izquierda", "derecha"]

ORIENTACION_INVERSA = {
    "derecha": "izquierda",
    "izquierda": "derecha",
    "arriba": "abajo",
    "abajo": "arriba"
}


def construir_id_enlace(id_pieza, lado):
    return f"{id_pieza}_{lado}"


class PuzzleDB:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.username = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE")

        variables_faltantes = [
            nombre
            for nombre, valor in {
                "NEO4J_URI": self.uri,
                "NEO4J_USERNAME": self.username,
                "NEO4J_PASSWORD": self.password,
                "NEO4J_DATABASE": self.database
            }.items()
            if not valor
        ]

        if variables_faltantes:
            raise ValueError(
                "Faltan variables en el archivo .env: "
                + ", ".join(variables_faltantes)
            )

        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password)
        )

    def close(self):
        self.driver.close()

    def crear_restricciones(self):
        queries = [
            """
            CREATE CONSTRAINT rompecabezas_id IF NOT EXISTS
            FOR (r:Rompecabezas)
            REQUIRE r.id_rompecabezas IS UNIQUE
            """,
            """
            CREATE CONSTRAINT pieza_id IF NOT EXISTS
            FOR (p:Pieza)
            REQUIRE p.id_pieza IS UNIQUE
            """,
            """
            CREATE CONSTRAINT enlace_id IF NOT EXISTS
            FOR (e:Enlace)
            REQUIRE e.id_enlace IS UNIQUE
            """
        ]

        with self.driver.session(database=self.database) as session:
            for query in queries:
                session.run(query)

    def limpiar_rompecabezas(self, id_rompecabezas):
        query = """
        MATCH (n)
        WHERE coalesce(n.id_rompecabezas, "") = $id_rompecabezas
           OR coalesce(n.id_pieza, "") STARTS WITH $prefijo
           OR coalesce(n.id_enlace, "") STARTS WITH $prefijo
        DETACH DELETE n
        """

        with self.driver.session(database=self.database) as session:
            session.run(
                query,
                id_rompecabezas=id_rompecabezas,
                prefijo=f"{id_rompecabezas}_"
            )

    def crear_rompecabezas(self, rompecabezas):
        query = """
        MERGE (r:Rompecabezas {id_rompecabezas: $id_rompecabezas})
        SET r.nombre = $nombre,
            r.marca = $marca,
            r.material = $material,
            r.tematica = $tematica,
            r.tipo = $tipo,
            r.descripcion = $descripcion,
            r.fecha_registro = date()
        """

        with self.driver.session(database=self.database) as session:
            session.run(query, **rompecabezas)

    def crear_pieza(self, id_rompecabezas, pieza):
        query = """
        MATCH (r:Rompecabezas {id_rompecabezas: $id_rompecabezas})
        MERGE (p:Pieza {id_pieza: $id_pieza})
        SET p.index = $index,
            p.nombre = $nombre,
            p.presente = $presente,
            p.fila = $fila,
            p.columna = $columna,
            p.x_relativo = $x_relativo,
            p.y_relativo = $y_relativo,
            p.color_principal = $color_principal,
            p.observaciones = $observaciones
        MERGE (r)-[rel:CONTIENE_PIEZA]->(p)
        SET rel.orden = $index
        """

        params = {"id_rompecabezas": id_rompecabezas, **pieza}

        with self.driver.session(database=self.database) as session:
            session.run(query, **params)

    def crear_enlace(self, id_pieza, enlace):
        query = """
        MATCH (p:Pieza {id_pieza: $id_pieza})
        MERGE (e:Enlace {id_enlace: $id_enlace})
        SET e.id_pieza = $id_pieza,
            e.lado = $lado,
            e.tipo = $tipo,
            e.forma = $forma,
            e.descripcion = $descripcion
        MERGE (p)-[rel:TIENE_ENLACE]->(e)
        SET rel.lado = $lado
        """

        params = {"id_pieza": id_pieza, **enlace}

        with self.driver.session(database=self.database) as session:
            session.run(query, **params)

    def crear_enlaces_basicos_pieza(
        self,
        id_pieza,
        tipos_por_lado=None,
        formas_por_lado=None
    ):
        tipos_por_lado = tipos_por_lado or {}
        formas_por_lado = formas_por_lado or {}

        for lado in LADOS_BASICOS:
            enlace = {
                "id_enlace": construir_id_enlace(id_pieza, lado),
                "lado": lado,
                "tipo": tipos_por_lado.get(lado, "sin_definir"),
                "forma": formas_por_lado.get(lado, "sin_definir"),
                "descripcion": f"Enlace {lado} de {id_pieza}"
            }

            self.crear_enlace(id_pieza, enlace)

    def conectar_enlaces(
        self,
        id_enlace_origen,
        id_enlace_destino,
        orientacion,
        tipo_contacto="contacto_fisico",
        descripcion="",
        crear_inversa=True
    ):
        query = """
        MATCH (e1:Enlace {id_enlace: $id_enlace_origen})
        MATCH (e2:Enlace {id_enlace: $id_enlace_destino})
        MERGE (e1)-[rel:ENCAJA_CON]->(e2)
        SET rel.orientacion = $orientacion,
            rel.tipo_contacto = $tipo_contacto,
            rel.descripcion = $descripcion,
            rel.requerido = true
        """

        with self.driver.session(database=self.database) as session:
            session.run(
                query,
                id_enlace_origen=id_enlace_origen,
                id_enlace_destino=id_enlace_destino,
                orientacion=orientacion,
                tipo_contacto=tipo_contacto,
                descripcion=descripcion
            )

        if crear_inversa and orientacion in ORIENTACION_INVERSA:
            self.conectar_enlaces(
                id_enlace_origen=id_enlace_destino,
                id_enlace_destino=id_enlace_origen,
                orientacion=ORIENTACION_INVERSA[orientacion],
                tipo_contacto=tipo_contacto,
                descripcion=f"Relación inversa de: {descripcion}",
                crear_inversa=False
            )

    def conectar_piezas_por_lados(
        self,
        id_pieza_origen,
        lado_origen,
        id_pieza_destino,
        lado_destino,
        orientacion=None,
        tipo_contacto="contacto_fisico",
        descripcion=""
    ):
        id_enlace_origen = construir_id_enlace(id_pieza_origen, lado_origen)
        id_enlace_destino = construir_id_enlace(id_pieza_destino, lado_destino)

        self.conectar_enlaces(
            id_enlace_origen=id_enlace_origen,
            id_enlace_destino=id_enlace_destino,
            orientacion=orientacion or lado_origen,
            tipo_contacto=tipo_contacto,
            descripcion=descripcion
        )

    def mostrar_resumen_carga(self, id_rompecabezas):
        query = """
        MATCH (r:Rompecabezas {id_rompecabezas: $id_rompecabezas})
        OPTIONAL MATCH (r)-[:CONTIENE_PIEZA]->(p:Pieza)
        OPTIONAL MATCH (p)-[:TIENE_ENLACE]->(e:Enlace)
        OPTIONAL MATCH (e)-[rel:ENCAJA_CON]->(:Enlace)
        RETURN r.nombre AS nombre,
               count(DISTINCT p) AS total_piezas,
               count(DISTINCT e) AS total_enlaces,
               count(DISTINCT rel) AS total_conexiones
        """

        with self.driver.session(database=self.database) as session:
            record = session.run(
                query,
                id_rompecabezas=id_rompecabezas
            ).single()

            print("Resumen de carga")
            print("----------------")
            print("Rompecabezas:", record["nombre"])
            print("Total de piezas:", record["total_piezas"])
            print("Total de enlaces:", record["total_enlaces"])
            print("Total de conexiones entre enlaces:", record["total_conexiones"])


def cargar_oso(db):
    id_rompecabezas = "oso_001"

    rompecabezas = {
        "id_rompecabezas": id_rompecabezas,
        "nombre": "Rompecabezas del oso",
        "marca": "Sin marca",
        "material": "Madera",
        "tematica": "Oso",
        "tipo": "Infantil",
        "descripcion": "Rompecabezas físico de oso compuesto por 9 piezas."
    }

    db.crear_rompecabezas(rompecabezas)

    piezas = [
        {
            "id_pieza": "oso_001_pieza_1",
            "index": 1,
            "nombre": "Pieza 1",
            "presente": True,
            "fila": 3,
            "columna": 1,
            "x_relativo": 0.0,
            "y_relativo": 2.0,
            "color_principal": "café",
            "observaciones": "Pata inferior izquierda del oso"
        },
        {
            "id_pieza": "oso_001_pieza_2",
            "index": 2,
            "nombre": "Pieza 2",
            "presente": True,
            "fila": 3,
            "columna": 2,
            "x_relativo": 1.0,
            "y_relativo": 2.0,
            "color_principal": "beige",
            "observaciones": "Parte inferior central del cuerpo"
        },
        {
            "id_pieza": "oso_001_pieza_3",
            "index": 3,
            "nombre": "Pieza 3",
            "presente": True,
            "fila": 3,
            "columna": 3,
            "x_relativo": 2.0,
            "y_relativo": 2.0,
            "color_principal": "café",
            "observaciones": "Pata inferior derecha del oso"
        },
        {
            "id_pieza": "oso_001_pieza_4",
            "index": 4,
            "nombre": "Pieza 4",
            "presente": True,
            "fila": 2,
            "columna": 1,
            "x_relativo": 0.0,
            "y_relativo": 1.0,
            "color_principal": "café",
            "observaciones": "Parte lateral izquierda del cuerpo"
        },
        {
            "id_pieza": "oso_001_pieza_5",
            "index": 5,
            "nombre": "Pieza 5",
            "presente": True,
            "fila": 2,
            "columna": 2,
            "x_relativo": 1.0,
            "y_relativo": 1.0,
            "color_principal": "beige",
            "observaciones": "Parte central del cuerpo y rostro pequeño"
        },
        {
            "id_pieza": "oso_001_pieza_6",
            "index": 6,
            "nombre": "Pieza 6",
            "presente": True,
            "fila": 2,
            "columna": 3,
            "x_relativo": 2.0,
            "y_relativo": 1.0,
            "color_principal": "café",
            "observaciones": "Parte lateral derecha del cuerpo"
        },
        {
            "id_pieza": "oso_001_pieza_7",
            "index": 7,
            "nombre": "Pieza 7",
            "presente": True,
            "fila": 1,
            "columna": 3,
            "x_relativo": 2.0,
            "y_relativo": 0.0,
            "color_principal": "café",
            "observaciones": "Cabeza derecha del oso"
        },
        {
            "id_pieza": "oso_001_pieza_8",
            "index": 8,
            "nombre": "Pieza 8",
            "presente": True,
            "fila": 1,
            "columna": 2,
            "x_relativo": 1.0,
            "y_relativo": 0.0,
            "color_principal": "café",
            "observaciones": "Cabeza grande izquierda del oso"
        },
        {
            "id_pieza": "oso_001_pieza_9",
            "index": 9,
            "nombre": "Pieza 9",
            "presente": True,
            "fila": 1,
            "columna": 4,
            "x_relativo": 3.0,
            "y_relativo": 0.0,
            "color_principal": "beige",
            "observaciones": "Pieza superior derecha del oso"
        }
    ]

    for pieza in piezas:
        db.crear_pieza(id_rompecabezas, pieza)

    conexiones = [
        {
            "id_pieza_origen": "oso_001_pieza_1",
            "lado_origen": "derecha",
            "id_pieza_destino": "oso_001_pieza_2",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 1 se conecta con la pieza 2 por el lado derecho."
        },
        {
            "id_pieza_origen": "oso_001_pieza_1",
            "lado_origen": "arriba",
            "id_pieza_destino": "oso_001_pieza_4",
            "lado_destino": "abajo",
            "orientacion": "arriba",
            "descripcion": "La pieza 1 se conecta con la pieza 4 por la parte superior."
        },
        {
            "id_pieza_origen": "oso_001_pieza_2",
            "lado_origen": "arriba",
            "id_pieza_destino": "oso_001_pieza_5",
            "lado_destino": "abajo",
            "orientacion": "arriba",
            "descripcion": "La pieza 2 se conecta con la pieza 5 por la parte superior."
        },
        {
            "id_pieza_origen": "oso_001_pieza_2",
            "lado_origen": "derecha",
            "id_pieza_destino": "oso_001_pieza_3",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 2 se conecta con la pieza 3 por el lado derecho."
        },
        {
            "id_pieza_origen": "oso_001_pieza_3",
            "lado_origen": "arriba",
            "id_pieza_destino": "oso_001_pieza_6",
            "lado_destino": "abajo",
            "orientacion": "arriba",
            "descripcion": "La pieza 3 se conecta con la pieza 6 por la parte superior."
        },
        {
            "id_pieza_origen": "oso_001_pieza_4",
            "lado_origen": "derecha",
            "id_pieza_destino": "oso_001_pieza_5",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 4 se conecta con la pieza 5 por el lado derecho."
        },
        {
            "id_pieza_origen": "oso_001_pieza_4",
            "lado_origen": "arriba",
            "id_pieza_destino": "oso_001_pieza_8",
            "lado_destino": "abajo_izquierda",
            "orientacion": "arriba",
            "descripcion": "La pieza 4 se conecta con la pieza 8 por la parte superior izquierda."
        },
        {
            "id_pieza_origen": "oso_001_pieza_5",
            "lado_origen": "derecha",
            "id_pieza_destino": "oso_001_pieza_6",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 5 se conecta con la pieza 6 por el lado derecho."
        },
        {
            "id_pieza_origen": "oso_001_pieza_5",
            "lado_origen": "arriba",
            "id_pieza_destino": "oso_001_pieza_8",
            "lado_destino": "abajo",
            "orientacion": "arriba",
            "descripcion": "La pieza 5 se conecta con la pieza 8 por la parte superior."
        },
        {
            "id_pieza_origen": "oso_001_pieza_5",
            "lado_origen": "arriba_derecha",
            "id_pieza_destino": "oso_001_pieza_7",
            "lado_destino": "abajo_izquierda",
            "orientacion": "arriba_derecha",
            "descripcion": "La pieza 5 se conecta con la pieza 7 por la parte superior derecha."
        },
        {
            "id_pieza_origen": "oso_001_pieza_6",
            "lado_origen": "arriba",
            "id_pieza_destino": "oso_001_pieza_7",
            "lado_destino": "abajo",
            "orientacion": "arriba",
            "descripcion": "La pieza 6 se conecta con la pieza 7 por la parte superior."
        },
        {
            "id_pieza_origen": "oso_001_pieza_7",
            "lado_origen": "izquierda",
            "id_pieza_destino": "oso_001_pieza_8",
            "lado_destino": "derecha",
            "orientacion": "izquierda",
            "descripcion": "La pieza 7 se conecta con la pieza 8 por el lado izquierdo."
        },
        {
            "id_pieza_origen": "oso_001_pieza_7",
            "lado_origen": "arriba",
            "id_pieza_destino": "oso_001_pieza_9",
            "lado_destino": "abajo",
            "orientacion": "arriba",
            "descripcion": "La pieza 7 se conecta con la pieza 9 por la parte superior."
        },
        {
            "id_pieza_origen": "oso_001_pieza_8",
            "lado_origen": "derecha_superior",
            "id_pieza_destino": "oso_001_pieza_9",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 8 se conecta con la pieza 9 por la parte derecha superior."
        }
    ]

    enlaces_creados = set()

    for conexion in conexiones:
        enlace_origen = {
            "id_enlace": construir_id_enlace(
                conexion["id_pieza_origen"],
                conexion["lado_origen"]
            ),
            "lado": conexion["lado_origen"],
            "tipo": "conexion",
            "forma": "irregular",
            "descripcion": (
                "Enlace "
                + conexion["lado_origen"]
                + " de "
                + conexion["id_pieza_origen"]
            )
        }

        enlace_destino = {
            "id_enlace": construir_id_enlace(
                conexion["id_pieza_destino"],
                conexion["lado_destino"]
            ),
            "lado": conexion["lado_destino"],
            "tipo": "conexion",
            "forma": "irregular",
            "descripcion": (
                "Enlace "
                + conexion["lado_destino"]
                + " de "
                + conexion["id_pieza_destino"]
            )
        }

        if enlace_origen["id_enlace"] not in enlaces_creados:
            db.crear_enlace(conexion["id_pieza_origen"], enlace_origen)
            enlaces_creados.add(enlace_origen["id_enlace"])

        if enlace_destino["id_enlace"] not in enlaces_creados:
            db.crear_enlace(conexion["id_pieza_destino"], enlace_destino)
            enlaces_creados.add(enlace_destino["id_enlace"])

        db.conectar_piezas_por_lados(**conexion)

def cargar_bus(db):
    id_rompecabezas = "bus_001"

    rompecabezas = {
        "id_rompecabezas": id_rompecabezas,
        "nombre": "Rompecabezas del bus escolar",
        "marca": "Sin marca",
        "material": "Madera",
        "tematica": "Bus escolar",
        "tipo": "Infantil",
        "descripcion": "Rompecabezas físico de bus escolar compuesto por 10 piezas. Las piezas 1 y 8 están registradas como faltantes."
    }

    db.crear_rompecabezas(rompecabezas)

    piezas = [
        {
            "id_pieza": "bus_001_pieza_1",
            "index": 1,
            "nombre": "Pieza 1",
            "presente": False,
            "fila": 1,
            "columna": 1,
            "x_relativo": 0.0,
            "y_relativo": 0.0,
            "color_principal": "amarillo",
            "observaciones": "Parte superior izquierda del bus con ventana del dinosaurio. Pieza faltante."
        },
        {
            "id_pieza": "bus_001_pieza_2",
            "index": 2,
            "nombre": "Pieza 2",
            "presente": True,
            "fila": 2,
            "columna": 1,
            "x_relativo": 0.0,
            "y_relativo": 1.0,
            "color_principal": "azul",
            "observaciones": "Parte inferior izquierda/frontal del bus."
        },
        {
            "id_pieza": "bus_001_pieza_3",
            "index": 3,
            "nombre": "Pieza 3",
            "presente": True,
            "fila": 3,
            "columna": 1,
            "x_relativo": 0.0,
            "y_relativo": 2.0,
            "color_principal": "negro",
            "observaciones": "Llanta delantera del bus."
        },
        {
            "id_pieza": "bus_001_pieza_4",
            "index": 4,
            "nombre": "Pieza 4",
            "presente": True,
            "fila": 1,
            "columna": 2,
            "x_relativo": 1.0,
            "y_relativo": 0.0,
            "color_principal": "rojo",
            "observaciones": "Parte superior central con puertas."
        },
        {
            "id_pieza": "bus_001_pieza_5",
            "index": 5,
            "nombre": "Pieza 5",
            "presente": True,
            "fila": 2,
            "columna": 2,
            "x_relativo": 1.0,
            "y_relativo": 1.0,
            "color_principal": "naranja",
            "observaciones": "Parte inferior central con puerta del bus."
        },
        {
            "id_pieza": "bus_001_pieza_6",
            "index": 6,
            "nombre": "Pieza 6",
            "presente": True,
            "fila": 1,
            "columna": 3,
            "x_relativo": 2.0,
            "y_relativo": 0.0,
            "color_principal": "verde",
            "observaciones": "Parte superior central derecha con ventanas."
        },
        {
            "id_pieza": "bus_001_pieza_7",
            "index": 7,
            "nombre": "Pieza 7",
            "presente": True,
            "fila": 2,
            "columna": 3,
            "x_relativo": 2.0,
            "y_relativo": 1.0,
            "color_principal": "amarillo",
            "observaciones": "Parte inferior central derecha con texto SCHOOL."
        },
        {
            "id_pieza": "bus_001_pieza_8",
            "index": 8,
            "nombre": "Pieza 8",
            "presente": False,
            "fila": 1,
            "columna": 4,
            "x_relativo": 3.0,
            "y_relativo": 0.0,
            "color_principal": "celeste",
            "observaciones": "Parte superior derecha del bus con ventana del oso. Pieza faltante."
        },
        {
            "id_pieza": "bus_001_pieza_9",
            "index": 9,
            "nombre": "Pieza 9",
            "presente": True,
            "fila": 2,
            "columna": 4,
            "x_relativo": 3.0,
            "y_relativo": 1.0,
            "color_principal": "azul",
            "observaciones": "Parte trasera derecha del bus."
        },
        {
            "id_pieza": "bus_001_pieza_10",
            "index": 10,
            "nombre": "Pieza 10",
            "presente": True,
            "fila": 3,
            "columna": 4,
            "x_relativo": 3.0,
            "y_relativo": 2.0,
            "color_principal": "negro",
            "observaciones": "Llanta trasera del bus."
        }
    ]

    for pieza in piezas:
        db.crear_pieza(id_rompecabezas, pieza)

    conexiones = [
        {
            "id_pieza_origen": "bus_001_pieza_1",
            "lado_origen": "derecha",
            "id_pieza_destino": "bus_001_pieza_4",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 1 se conecta con la pieza 4 por el lado derecho."
        },
        {
            "id_pieza_origen": "bus_001_pieza_1",
            "lado_origen": "abajo",
            "id_pieza_destino": "bus_001_pieza_2",
            "lado_destino": "arriba",
            "orientacion": "abajo",
            "descripcion": "La pieza 1 se conecta con la pieza 2 por la parte inferior."
        },
        {
            "id_pieza_origen": "bus_001_pieza_2",
            "lado_origen": "derecha",
            "id_pieza_destino": "bus_001_pieza_5",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 2 se conecta con la pieza 5 por el lado derecho."
        },
        {
            "id_pieza_origen": "bus_001_pieza_2",
            "lado_origen": "abajo",
            "id_pieza_destino": "bus_001_pieza_3",
            "lado_destino": "arriba",
            "orientacion": "abajo",
            "descripcion": "La pieza 2 se conecta con la pieza 3 por la parte inferior."
        },
        {
            "id_pieza_origen": "bus_001_pieza_3",
            "lado_origen": "derecha_superior",
            "id_pieza_destino": "bus_001_pieza_5",
            "lado_destino": "izquierda_inferior",
            "orientacion": "derecha",
            "descripcion": "La pieza 3 se conecta con la pieza 5 en la zona inferior izquierda."
        },
        {
            "id_pieza_origen": "bus_001_pieza_4",
            "lado_origen": "abajo",
            "id_pieza_destino": "bus_001_pieza_5",
            "lado_destino": "arriba",
            "orientacion": "abajo",
            "descripcion": "La pieza 4 se conecta con la pieza 5 por la parte inferior."
        },
        {
            "id_pieza_origen": "bus_001_pieza_4",
            "lado_origen": "derecha",
            "id_pieza_destino": "bus_001_pieza_6",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 4 se conecta con la pieza 6 por el lado derecho."
        },
        {
            "id_pieza_origen": "bus_001_pieza_5",
            "lado_origen": "derecha",
            "id_pieza_destino": "bus_001_pieza_7",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 5 se conecta con la pieza 7 por el lado derecho."
        },
        {
            "id_pieza_origen": "bus_001_pieza_6",
            "lado_origen": "abajo",
            "id_pieza_destino": "bus_001_pieza_7",
            "lado_destino": "arriba",
            "orientacion": "abajo",
            "descripcion": "La pieza 6 se conecta con la pieza 7 por la parte inferior."
        },
        {
            "id_pieza_origen": "bus_001_pieza_6",
            "lado_origen": "derecha",
            "id_pieza_destino": "bus_001_pieza_8",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 6 se conecta con la pieza 8 por el lado derecho."
        },
        {
            "id_pieza_origen": "bus_001_pieza_7",
            "lado_origen": "derecha",
            "id_pieza_destino": "bus_001_pieza_9",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 7 se conecta con la pieza 9 por el lado derecho."
        },
        {
            "id_pieza_origen": "bus_001_pieza_7",
            "lado_origen": "abajo_derecha",
            "id_pieza_destino": "bus_001_pieza_10",
            "lado_destino": "arriba_izquierda",
            "orientacion": "abajo",
            "descripcion": "La pieza 7 se conecta con la pieza 10 en la parte inferior derecha."
        },
        {
            "id_pieza_origen": "bus_001_pieza_8",
            "lado_origen": "abajo",
            "id_pieza_destino": "bus_001_pieza_9",
            "lado_destino": "arriba",
            "orientacion": "abajo",
            "descripcion": "La pieza 8 se conecta con la pieza 9 por la parte inferior."
        },
        {
            "id_pieza_origen": "bus_001_pieza_9",
            "lado_origen": "abajo",
            "id_pieza_destino": "bus_001_pieza_10",
            "lado_destino": "arriba",
            "orientacion": "abajo",
            "descripcion": "La pieza 9 se conecta con la pieza 10 por la parte inferior."
        }
    ]

    enlaces_creados = set()

    for conexion in conexiones:
        enlace_origen = {
            "id_enlace": construir_id_enlace(
                conexion["id_pieza_origen"],
                conexion["lado_origen"]
            ),
            "lado": conexion["lado_origen"],
            "tipo": "conexion",
            "forma": "irregular",
            "descripcion": (
                "Enlace "
                + conexion["lado_origen"]
                + " de "
                + conexion["id_pieza_origen"]
            )
        }

        enlace_destino = {
            "id_enlace": construir_id_enlace(
                conexion["id_pieza_destino"],
                conexion["lado_destino"]
            ),
            "lado": conexion["lado_destino"],
            "tipo": "conexion",
            "forma": "irregular",
            "descripcion": (
                "Enlace "
                + conexion["lado_destino"]
                + " de "
                + conexion["id_pieza_destino"]
            )
        }

        if enlace_origen["id_enlace"] not in enlaces_creados:
            db.crear_enlace(conexion["id_pieza_origen"], enlace_origen)
            enlaces_creados.add(enlace_origen["id_enlace"])

        if enlace_destino["id_enlace"] not in enlaces_creados:
            db.crear_enlace(conexion["id_pieza_destino"], enlace_destino)
            enlaces_creados.add(enlace_destino["id_enlace"])

        db.conectar_piezas_por_lados(**conexion) 



def cargar_zorro(db):
    id_rompecabezas = "zorro_001"

    rompecabezas = {
        "id_rompecabezas": id_rompecabezas,
        "nombre": "Rompecabezas de la familia de zorros",
        "marca": "Sin marca",
        "material": "Madera",
        "tematica": "Familia de zorros",
        "tipo": "Infantil",
        "descripcion": (
            "Rompecabezas físico de madera con la imagen "
            "de una familia de zorros compuesto por 10 piezas."
        )
    }

    db.crear_rompecabezas(rompecabezas)

    piezas = [
        {
            "id_pieza": "zorro_001_pieza_1",
            "index": 1,
            "nombre": "Pieza 1",
            "presente": True,
            "fila": 1,
            "columna": 1,
            "x_relativo": 0.0,
            "y_relativo": 0.0,
            "color_principal": "rojo oscuro",
            "observaciones": "Cabeza y cuerpo superior de la zorra mamá, lado izquierdo"
        },
        {
            "id_pieza": "zorro_001_pieza_2",
            "index": 2,
            "nombre": "Pieza 2",
            "presente": True,
            "fila": 2,
            "columna": 1,
            "x_relativo": 0.0,
            "y_relativo": 1.0,
            "color_principal": "naranja rojizo",
            "observaciones": "Cuerpo grande y cola enrollada de la zorra mamá"
        },
        {
            "id_pieza": "zorro_001_pieza_3",
            "index": 3,
            "nombre": "Pieza 3",
            "presente": True,
            "fila": 3,
            "columna": 1,
            "x_relativo": 0.0,
            "y_relativo": 2.0,
            "color_principal": "naranja rojizo",
            "observaciones": "Base inferior izquierda, parte de la cola de la mamá"
        },
        {
            "id_pieza": "zorro_001_pieza_4",
            "index": 4,
            "nombre": "Pieza 4",
            "presente": True,
            "fila": 1,
            "columna": 2,
            "x_relativo": 1.0,
            "y_relativo": 0.0,
            "color_principal": "naranja",
            "observaciones": "Cabeza del zorro papá central con frente naranja brillante"
        },
        {
            "id_pieza": "zorro_001_pieza_5",
            "index": 5,
            "nombre": "Pieza 5",
            "presente": True,
            "fila": 2,
            "columna": 2,
            "x_relativo": 1.0,
            "y_relativo": 1.0,
            "color_principal": "naranja rojizo",
            "observaciones": "Cuerpo central del zorro papá"
        },
        {
            "id_pieza": "zorro_001_pieza_6",
            "index": 6,
            "nombre": "Pieza 6",
            "presente": True,
            "fila": 2,
            "columna": 3,
            "x_relativo": 2.0,
            "y_relativo": 1.0,
            "color_principal": "naranja rojizo",
            "observaciones": "Cola central y parte lateral derecha del zorro papá"
        },
        {
            "id_pieza": "zorro_001_pieza_7",
            "index": 7,
            "nombre": "Pieza 7",
            "presente": True,
            "fila": 3,
            "columna": 2,
            "x_relativo": 1.0,
            "y_relativo": 2.0,
            "color_principal": "rosa claro",
            "observaciones": "Final de la cola de la mamá y parte inferior del cuerpo del zorro papá"
        },
        {
            "id_pieza": "zorro_001_pieza_8",
            "index": 8,
            "nombre": "Pieza 8",
            "presente": True,
            "fila": 1,
            "columna": 3,
            "x_relativo": 2.0,
            "y_relativo": 0.0,
            "color_principal": "rosado salmón",
            "observaciones": "Cabeza y cara del zorro pequeño derecho"
        },
        {
            "id_pieza": "zorro_001_pieza_9",
            "index": 9,
            "nombre": "Pieza 9",
            "presente": True,
            "fila": 3,
            "columna": 3,
            "x_relativo": 2.0,
            "y_relativo": 2.0,
            "color_principal": "naranja salmón",
            "observaciones": "Base inferior del zorro pequeño derecho"
        },
        {
            "id_pieza": "zorro_001_pieza_10",
            "index": 10,
            "nombre": "Pieza 10",
            "presente": True,
            "fila": 2,
            "columna": 4,
            "x_relativo": 3.0,
            "y_relativo": 1.0,
            "color_principal": "naranja con blanco",
            "observaciones": "Cola grande derecha del zorro pequeño con punta blanca"
        }
    ]

    for pieza in piezas:
        db.crear_pieza(id_rompecabezas, pieza)

    conexiones = [
        {
            "id_pieza_origen": "zorro_001_pieza_1",
            "lado_origen": "derecha",
            "id_pieza_destino": "zorro_001_pieza_4",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 1 (mamá) encaja con la pieza 4 (cabeza papá) por el lado derecho."
        },
        {
            "id_pieza_origen": "zorro_001_pieza_1",
            "lado_origen": "abajo",
            "id_pieza_destino": "zorro_001_pieza_2",
            "lado_destino": "arriba",
            "orientacion": "abajo",
            "descripcion": "La pieza 1 (cabeza mamá) encaja con la pieza 2 (cuerpo mamá) por la parte inferior."
        },
        {
            "id_pieza_origen": "zorro_001_pieza_2",
            "lado_origen": "derecha",
            "id_pieza_destino": "zorro_001_pieza_5",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 2 (cuerpo mamá) encaja con la pieza 5 (cuerpo papá) por el lado derecho."
        },
        {
            "id_pieza_origen": "zorro_001_pieza_2",
            "lado_origen": "abajo",
            "id_pieza_destino": "zorro_001_pieza_3",
            "lado_destino": "arriba",
            "orientacion": "abajo",
            "descripcion": "La pieza 2 (cuerpo mamá) encaja con la pieza 3 (base izquierda) por la parte inferior."
        },
        {
            "id_pieza_origen": "zorro_001_pieza_3",
            "lado_origen": "derecha",
            "id_pieza_destino": "zorro_001_pieza_7",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 3 (base izquierda) encaja con la pieza 7 (base central) por el lado derecho."
        },
        {
            "id_pieza_origen": "zorro_001_pieza_4",
            "lado_origen": "abajo",
            "id_pieza_destino": "zorro_001_pieza_5",
            "lado_destino": "arriba",
            "orientacion": "abajo",
            "descripcion": "La pieza 4 (cabeza papá) encaja con la pieza 5 (cuerpo papá) por la parte inferior."
        },
        {
            "id_pieza_origen": "zorro_001_pieza_4",
            "lado_origen": "derecha",
            "id_pieza_destino": "zorro_001_pieza_8",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 4 (cabeza papá) encaja con la pieza 8 (cabeza zorro pequeño) por el lado derecho."
        },
        {
            "id_pieza_origen": "zorro_001_pieza_5",
            "lado_origen": "derecha",
            "id_pieza_destino": "zorro_001_pieza_6",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 5 (cuerpo papá) encaja con la pieza 6 (cola central) por el lado derecho."
        },
        {
            "id_pieza_origen": "zorro_001_pieza_5",
            "lado_origen": "abajo",
            "id_pieza_destino": "zorro_001_pieza_7",
            "lado_destino": "arriba",
            "orientacion": "abajo",
            "descripcion": "La pieza 5 (cuerpo papá) encaja con la pieza 7 (base central) por la parte inferior."
        },
        {
            "id_pieza_origen": "zorro_001_pieza_6",
            "lado_origen": "arriba",
            "id_pieza_destino": "zorro_001_pieza_8",
            "lado_destino": "abajo_izquierda",
            "orientacion": "arriba",
            "descripcion": "La pieza 6 (cola central) encaja con la pieza 8 (zorro pequeño) por la parte superior derecha."
        },
        {
            "id_pieza_origen": "zorro_001_pieza_6",
            "lado_origen": "abajo",
            "id_pieza_destino": "zorro_001_pieza_7",
            "lado_destino": "derecha",
            "orientacion": "abajo",
            "descripcion": "La pieza 6 (cola central) encaja con la pieza 7 (base central) por la parte inferior derecha."
        },
        {
            "id_pieza_origen": "zorro_001_pieza_7",
            "lado_origen": "derecha",
            "id_pieza_destino": "zorro_001_pieza_9",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 7 (base central) encaja con la pieza 9 (base derecha) por el lado derecho."
        },
        {
            "id_pieza_origen": "zorro_001_pieza_8",
            "lado_origen": "abajo",
            "id_pieza_destino": "zorro_001_pieza_9",
            "lado_destino": "arriba",
            "orientacion": "abajo",
            "descripcion": "La pieza 8 (cabeza zorro pequeño) encaja con la pieza 9 (base derecha) por la parte inferior."
        },
        {
            "id_pieza_origen": "zorro_001_pieza_8",
            "lado_origen": "derecha",
            "id_pieza_destino": "zorro_001_pieza_10",
            "lado_destino": "izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 8 (zorro pequeño) encaja con la pieza 10 (cola derecha) por el lado derecho."
        },
        {
            "id_pieza_origen": "zorro_001_pieza_9",
            "lado_origen": "derecha",
            "id_pieza_destino": "zorro_001_pieza_10",
            "lado_destino": "abajo_izquierda",
            "orientacion": "derecha",
            "descripcion": "La pieza 9 (base derecha) encaja con la pieza 10 (cola derecha) por el lado derecho inferior."
        }
    ]

    enlaces_creados = set()

    for conexion in conexiones:
        enlace_origen = {
            "id_enlace": construir_id_enlace(
                conexion["id_pieza_origen"],
                conexion["lado_origen"]
            ),
            "lado": conexion["lado_origen"],
            "tipo": "conexion",
            "forma": "irregular",
            "descripcion": (
                "Enlace "
                + conexion["lado_origen"]
                + " de "
                + conexion["id_pieza_origen"]
            )
        }

        enlace_destino = {
            "id_enlace": construir_id_enlace(
                conexion["id_pieza_destino"],
                conexion["lado_destino"]
            ),
            "lado": conexion["lado_destino"],
            "tipo": "conexion",
            "forma": "irregular",
            "descripcion": (
                "Enlace "
                + conexion["lado_destino"]
                + " de "
                + conexion["id_pieza_destino"]
            )
        }

        if enlace_origen["id_enlace"] not in enlaces_creados:
            db.crear_enlace(conexion["id_pieza_origen"], enlace_origen)
            enlaces_creados.add(enlace_origen["id_enlace"])

        if enlace_destino["id_enlace"] not in enlaces_creados:
            db.crear_enlace(conexion["id_pieza_destino"], enlace_destino)
            enlaces_creados.add(enlace_destino["id_enlace"])

        db.conectar_piezas_por_lados(**conexion)



if __name__ == "__main__":
    db = PuzzleDB()

    try:
        db.crear_restricciones()

        db.limpiar_rompecabezas("oso_001")
        db.limpiar_rompecabezas("bus_001")
        db.limpiar_rompecabezas("zorro_001")

        cargar_oso(db)
        cargar_bus(db)
        cargar_zorro(db)

        db.mostrar_resumen_carga("oso_001")
        print()
        db.mostrar_resumen_carga("bus_001")
        print()
        db.mostrar_resumen_carga("zorro_001")

    finally:
        db.close()  