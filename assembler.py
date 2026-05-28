from neo4j import GraphDatabase
from dotenv import load_dotenv

from collections import deque
import os


# =========================================================
# CARGAR VARIABLES DE ENTORNO
# =========================================================

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")


# =========================================================
# CLASE PRINCIPAL
# =========================================================

class PuzzleAssembler:

    def __init__(self):

        self.driver = GraphDatabase.driver(
            URI,
            auth=(USER, PASSWORD)
        )

        # Piezas ya colocadas
        self.piezas_colocadas = set()

    # =====================================================
    # CERRAR DRIVER
    # =====================================================

    def close(self):
        self.driver.close()

    # =====================================================
    # OBTENER PRIMERA PIEZA DISPONIBLE
    # =====================================================

    def obtener_pieza_inicial(self, id_rompecabezas):

        query = """
        MATCH (r:Rompecabezas)-[:CONTIENE_PIEZA]->(p:Pieza)

        WHERE r.id_rompecabezas = $id_rompecabezas
          AND p.presente = true

        RETURN p
        ORDER BY p.index
        LIMIT 1
        """

        with self.driver.session() as session:

            result = session.run(
                query,
                id_rompecabezas=id_rompecabezas
            )

            record = result.single()

            if record:
                return dict(record["p"])

            return None

    # =====================================================
    # OBTENER CONEXIONES DE UNA PIEZA
    # =====================================================

    def obtener_conexiones(self, id_pieza):

        query = """
        MATCH (p1:Pieza {id_pieza: $id_pieza})
              -[t1:TIENE_ENLACE]->
              (e1:Enlace)
              -[r:ENCAJA_CON]-
              (e2:Enlace)
              <-[t2:TIENE_ENLACE]-
              (p2:Pieza)

        RETURN
            p2,

            t1.lado AS lado_actual,
            t2.lado AS lado_vecino,

            r.orientacion AS orientacion,
            r.tipo_contacto AS tipo_contacto,
            r.descripcion AS descripcion,
            r.requerido AS requerido

        ORDER BY p2.index
        """

        with self.driver.session() as session:

            result = session.run(
                query,
                id_pieza=id_pieza
            )

            conexiones = []

            for record in result:

                conexiones.append({

                    "pieza": dict(record["p2"]),

                    "lado_actual": record["lado_actual"],
                    "lado_vecino": record["lado_vecino"],

                    "orientacion": record["orientacion"],
                    "tipo_contacto": record["tipo_contacto"],
                    "descripcion": record["descripcion"],
                    "requerido": record["requerido"]
                })

            return conexiones

    # =====================================================
    # BUSCAR OTRA PIEZA DISPONIBLE NO COLOCADA
    # =====================================================

    def buscar_nueva_base(self, id_rompecabezas):

        query = """
        MATCH (r:Rompecabezas)-[:CONTIENE_PIEZA]->(p:Pieza)

        WHERE r.id_rompecabezas = $id_rompecabezas
          AND p.presente = true
          AND NOT p.id_pieza IN $colocadas

        RETURN p
        ORDER BY p.index
        LIMIT 1
        """

        with self.driver.session() as session:

            result = session.run(
                query,
                id_rompecabezas=id_rompecabezas,
                colocadas=list(self.piezas_colocadas)
            )

            record = result.single()

            if record:
                return dict(record["p"])

            return None

    # =====================================================
    # IMPRIMIR INFORMACION DE UNA PIEZA
    # =====================================================

    def imprimir_pieza_base(self, pieza):

        print("\n====================================")
        print("PIEZA BASE")
        print("====================================")

        print(f"ID PIEZA: {pieza['id_pieza']}")

        if pieza.get("nombre"):
            print(f"NOMBRE: {pieza['nombre']}")

        print(
            f"POSICION:"
            f" fila={pieza.get('fila')},"
            f" columna={pieza.get('columna')}"
        )

        print(
            f"COORDENADAS RELATIVAS:"
            f" x={pieza.get('x_relativo')},"
            f" y={pieza.get('y_relativo')}"
        )

    # =====================================================
    # IMPRIMIR INSTRUCCION DE ENSAMBLAJE
    # =====================================================

    def imprimir_instruccion(
        self,
        pieza_actual,
        conexion
    ):

        pieza_vecina = conexion["pieza"]

        print("\n------------------------------------")

        print(
            f"Conectar pieza "
            f"{pieza_vecina['id_pieza']}"
        )

        print(
            f"con la pieza "
            f"{pieza_actual['id_pieza']}"
        )

        print(
            f"Lado actual: "
            f"{conexion['lado_actual']}"
        )

        print(
            f"Lado vecino: "
            f"{conexion['lado_vecino']}"
        )

        print(
            f"Orientacion: "
            f"{conexion['orientacion']}"
        )

        print(
            f"Tipo contacto: "
            f"{conexion['tipo_contacto']}"
        )

        if conexion["descripcion"]:
            print(
                f"Descripcion: "
                f"{conexion['descripcion']}"
            )

        print(
            f"Posicion esperada:"
            f" fila={pieza_vecina.get('fila')},"
            f" columna={pieza_vecina.get('columna')}"
        )

        print(
            f"Coordenadas relativas:"
            f" x={pieza_vecina.get('x_relativo')},"
            f" y={pieza_vecina.get('y_relativo')}"
        )

        if conexion["requerido"]:
            print("Ensamblaje requerido: SI")
        else:
            print("Ensamblaje requerido: NO")

    # =====================================================
    # ALGORITMO PRINCIPAL
    # =====================================================

    def armar_rompecabezas(self, id_rompecabezas):

        print("\n====================================")
        print("INICIO DEL ARMADO")
        print("====================================")

        # -------------------------------------------------
        # Obtener primera pieza
        # -------------------------------------------------

        pieza_inicial = self.obtener_pieza_inicial(
            id_rompecabezas
        )

        if not pieza_inicial:

            print(
                "No existen piezas disponibles."
            )

            return

        # -------------------------------------------------
        # Cola BFS
        # -------------------------------------------------

        cola = deque()

        cola.append(pieza_inicial)

        self.piezas_colocadas.add(
            pieza_inicial["id_pieza"]
        )

        self.imprimir_pieza_base(
            pieza_inicial
        )

        # =================================================
        # LOOP PRINCIPAL
        # =================================================

        while True:

            # -------------------------------------------------
            # RECORRER COMPONENTE ACTUAL
            # -------------------------------------------------

            while cola:

                pieza_actual = cola.popleft()

                conexiones = self.obtener_conexiones(
                    pieza_actual["id_pieza"]
                )

                # ---------------------------------------------
                # RECORRER CONEXIONES
                # ---------------------------------------------

                for conexion in conexiones:

                    pieza_vecina = conexion["pieza"]

                    id_vecina = pieza_vecina["id_pieza"]

                    # -----------------------------------------
                    # PIEZA FALTANTE
                    # -----------------------------------------

                    if not pieza_vecina["presente"]:

                        print("\n------------------------------------")

                        print(
                            f"La pieza "
                            f"{id_vecina} "
                            f"NO esta disponible."
                        )

                        print(
                            "Se omite este enlace."
                        )

                        continue

                    # -----------------------------------------
                    # YA FUE COLOCADA
                    # -----------------------------------------

                    if id_vecina in self.piezas_colocadas:
                        continue

                    # -----------------------------------------
                    # IMPRIMIR INSTRUCCION
                    # -----------------------------------------

                    self.imprimir_instruccion(
                        pieza_actual,
                        conexion
                    )

                    # -----------------------------------------
                    # MARCAR COMO COLOCADA
                    # -----------------------------------------

                    self.piezas_colocadas.add(
                        id_vecina
                    )

                    cola.append(
                        pieza_vecina
                    )

            # -------------------------------------------------
            # BUSCAR NUEVA PIEZA BASE
            # -------------------------------------------------

            nueva_base = self.buscar_nueva_base(
                id_rompecabezas
            )

            # -------------------------------------------------
            # FIN DEL ROMPECABEZAS
            # -------------------------------------------------

            if not nueva_base:
                break

            print("\n====================================")
            print("NUEVA SECCION DEL ROMPECABEZAS")
            print("====================================")

            print(
                "\nSe detecto una nueva componente "
                "desconectada debido a piezas faltantes."
            )

            self.imprimir_pieza_base(
                nueva_base
            )

            self.piezas_colocadas.add(
                nueva_base["id_pieza"]
            )

            cola.append(
                nueva_base
            )

        # =================================================
        # FINALIZAR
        # =================================================

        print("\n====================================")
        print("ROMPECABEZAS COMPLETADO")
        print("====================================")

        print(
            f"\nTotal de piezas colocadas: "
            f"{len(self.piezas_colocadas)}"
        )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    assembler = PuzzleAssembler()

    assembler.armar_rompecabezas(
        id_rompecabezas="oso_001"
    )

    assembler.close()