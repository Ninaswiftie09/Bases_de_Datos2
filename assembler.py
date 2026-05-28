from neo4j import GraphDatabase
from dotenv import load_dotenv

from collections import deque
import os


# =========================================================
# CARGAR VARIABLES DE ENTORNO
# =========================================================

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")


# =========================================================
# UTILIDADES DE PRESENTACION
# =========================================================

def describir_posicion(fila, columna):
    """
    Convierte fila/columna en una descripción de posición
    legible para el usuario final.
    Asume que fila 1 = arriba, columna 1 = izquierda.
    """

    descripciones_fila = {
        1: "primera fila (arriba del todo)",
        2: "segunda fila",
        3: "tercera fila",
        4: "cuarta fila",
        5: "quinta fila",
    }

    descripciones_columna = {
        1: "primera columna (extremo izquierdo)",
        2: "segunda columna",
        3: "tercera columna",
        4: "cuarta columna",
        5: "quinta columna",
    }

    desc_fila = (
        descripciones_fila.get(fila)
        or f"fila {fila}"
    )

    desc_columna = (
        descripciones_columna.get(columna)
        or f"columna {columna}"
    )

    return f"{desc_fila}, {desc_columna}"


def describir_lado(lado):
    """
    Traduce el nombre técnico del lado a lenguaje natural.
    """

    traduccion = {
        "top":    "parte de arriba",
        "bottom": "parte de abajo",
        "left":   "lado izquierdo",
        "right":  "lado derecho",
        "norte":  "parte de arriba",
        "sur":    "parte de abajo",
        "oeste":  "lado izquierdo",
        "este":   "lado derecho",
    }

    return traduccion.get(
        str(lado).lower(),
        str(lado)
    )


def describir_orientacion(orientacion):
    """
    Traduce la orientación técnica a una instrucción
    comprensible para el usuario.
    """

    if not orientacion:
        return None

    traduccion = {
        "normal":     "sin rotación (tal como viene la pieza)",
        "rotado_90":  "girada 90° hacia la derecha",
        "rotado_180": "girada 180° (al revés)",
        "rotado_270": "girada 90° hacia la izquierda",
        "horizontal": "en posición horizontal",
        "vertical":   "en posición vertical",
    }

    return traduccion.get(
        str(orientacion).lower(),
        str(orientacion)
    )


def nombre_pieza(pieza):
    """
    Devuelve el nombre de la pieza si existe,
    o un número de referencia amigable en caso contrario.
    """

    if pieza.get("nombre"):
        return f'"{pieza["nombre"]}"'

    return f'#{pieza["id_pieza"]}'


# =========================================================
# CLASE PRINCIPAL
# =========================================================

class PuzzleAssembler:

    def __init__(self):

        self.driver = GraphDatabase.driver(
            URI,
            auth=(USER, PASSWORD)
        )

        # Piezas presentes ya colocadas (o encoladas)
        self.piezas_colocadas = set()

        # Piezas faltantes ya atravesadas para buscar
        # vecinos presentes al otro lado del hueco.
        # Evita procesar el mismo hueco más de una vez
        # si dos piezas presentes apuntan a él.
        self.faltantes_atravesadas = set()

        # Contador de pasos para el usuario
        self.paso = 0

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
    # (fallback cuando el grafo queda desconectado)
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
    # IMPRIMIR PIEZA BASE (punto de partida de sección)
    # =====================================================

    def imprimir_pieza_base(self, pieza, es_primera=True):

        fila    = pieza.get("fila")
        columna = pieza.get("columna")

        if es_primera:
            print("\n┌─────────────────────────────────────┐")
            print("│         PUNTO DE PARTIDA            │")
            print("└─────────────────────────────────────┘")
            print(
                f"\nToma la pieza {nombre_pieza(pieza)} "
                f"y colócala como punto de partida."
            )
        else:
            print("\n┌─────────────────────────────────────┐")
            print("│      SIGUIENTE PIEZA DE PARTIDA     │")
            print("└─────────────────────────────────────┘")
            print(
                f"\nToma la pieza {nombre_pieza(pieza)} "
                f"y colócala de forma independiente."
            )

        if fila is not None and columna is not None:
            posicion = describir_posicion(fila, columna)
            print(f"Ubícala en la {posicion}.")

    # =====================================================
    # IMPRIMIR INSTRUCCION DE ENSAMBLAJE
    # =====================================================

    def imprimir_instruccion(self, pieza_actual, conexion):

        self.paso += 1

        pieza_vecina = conexion["pieza"]
        lado_actual  = describir_lado(conexion["lado_actual"])
        lado_vecino  = describir_lado(conexion["lado_vecino"])
        orientacion  = describir_orientacion(conexion["orientacion"])
        descripcion  = conexion["descripcion"]
        requerido    = conexion["requerido"]

        fila    = pieza_vecina.get("fila")
        columna = pieza_vecina.get("columna")

        print(f"\n── Paso {self.paso} " + "─" * 30)

        print(
            f"Toma la pieza {nombre_pieza(pieza_vecina)} "
            f"y únela a la pieza {nombre_pieza(pieza_actual)}."
        )

        print(
            f"  • Encaja el {lado_vecino} de la pieza nueva "
            f"contra el {lado_actual} de la pieza anterior."
        )

        if orientacion:
            print(f"  • Orientación: {orientacion}.")

        if descripcion:
            print(f"  • {descripcion}.")

        if fila is not None and columna is not None:
            posicion = describir_posicion(fila, columna)
            print(f"  • Esta pieza quedará en la {posicion}.")

        if requerido:
            print("  ⚠ Este ensamblaje es obligatorio.")

    # =====================================================
    # ATRAVESAR PIEZA FALTANTE
    #
    # Cuando se encuentra un hueco (pieza no presente),
    # se consultan sus vecinas en el grafo. Toda vecina
    # presente que aún no fue colocada se encola como
    # nueva base (con su propia instrucción de posición),
    # garantizando que ninguna pieza presente quede
    # inaccesible por culpa del hueco.
    # =====================================================

    def atravesar_faltante(self, pieza_faltante, cola):

        id_faltante = pieza_faltante["id_pieza"]

        # Evitar reprocesar el mismo hueco
        if id_faltante in self.faltantes_atravesadas:
            return

        self.faltantes_atravesadas.add(id_faltante)

        print(
            f"\n  ℹ La pieza {nombre_pieza(pieza_faltante)} "
            f"no está disponible. "
            f"Se buscan piezas presentes al otro lado del hueco."
        )

        # Consultar vecinas de la pieza faltante
        conexiones_del_hueco = self.obtener_conexiones(
            id_faltante
        )

        nuevas_bases_encontradas = False

        for conexion in conexiones_del_hueco:

            vecina = conexion["pieza"]
            id_vecina = vecina["id_pieza"]

            # Solo interesa si está presente y no fue colocada
            if not vecina["presente"]:
                continue

            if id_vecina in self.piezas_colocadas:
                continue

            # -------------------------------------------------
            # Pieza presente encontrada al otro lado del hueco:
            # se trata como nueva base independiente.
            # -------------------------------------------------

            self.imprimir_pieza_base(
                vecina,
                es_primera=False
            )

            self.piezas_colocadas.add(id_vecina)
            cola.append(vecina)

            nuevas_bases_encontradas = True

        if not nuevas_bases_encontradas:
            print(
                "  No se encontraron piezas disponibles "
                "al otro lado de ese hueco."
            )

    # =====================================================
    # ALGORITMO PRINCIPAL
    # =====================================================

    def armar_rompecabezas(self, id_rompecabezas):

        print("\n╔═════════════════════════════════════╗")
        print("║     INSTRUCCIONES DE ARMADO         ║")
        print("╚═════════════════════════════════════╝")

        # -------------------------------------------------
        # Obtener primera pieza
        # -------------------------------------------------

        pieza_inicial = self.obtener_pieza_inicial(
            id_rompecabezas
        )

        if not pieza_inicial:

            print(
                "\nNo hay piezas disponibles "
                "para armar el rompecabezas."
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
            pieza_inicial,
            es_primera=True
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
                    id_vecina    = pieza_vecina["id_pieza"]

                    # -----------------------------------------
                    # PIEZA FALTANTE: atravesar el hueco para
                    # no perder piezas presentes al otro lado.
                    # -----------------------------------------

                    if not pieza_vecina["presente"]:

                        self.atravesar_faltante(
                            pieza_vecina,
                            cola
                        )

                        continue

                    # -----------------------------------------
                    # YA FUE COLOCADA
                    # -----------------------------------------

                    if id_vecina in self.piezas_colocadas:
                        continue

                    # -----------------------------------------
                    # PIEZA PRESENTE Y NUEVA: instrucción normal
                    # -----------------------------------------

                    self.imprimir_instruccion(
                        pieza_actual,
                        conexion
                    )

                    self.piezas_colocadas.add(id_vecina)
                    cola.append(pieza_vecina)

            # -------------------------------------------------
            # FALLBACK: buscar pieza aún no colocada.
            # Esto solo ocurre si el grafo tiene componentes
            # completamente aisladas (sin ninguna conexión
            # hacia el resto), lo cual es poco probable pero
            # posible en datos mal registrados.
            # -------------------------------------------------

            nueva_base = self.buscar_nueva_base(
                id_rompecabezas
            )

            if not nueva_base:
                break

            print("\n┌─────────────────────────────────────┐")
            print("│      GRUPO COMPLETAMENTE AISLADO    │")
            print("└─────────────────────────────────────┘")

            print(
                "\nSe encontró una pieza sin conexión "
                "hacia ninguna pieza ya procesada."
            )

            self.imprimir_pieza_base(
                nueva_base,
                es_primera=False
            )

            self.piezas_colocadas.add(
                nueva_base["id_pieza"]
            )

            cola.append(nueva_base)

        # =================================================
        # FINALIZAR
        # =================================================

        print("\n╔═════════════════════════════════════╗")
        print("║       ¡ROMPECABEZAS TERMINADO!      ║")
        print("╚═════════════════════════════════════╝")

        print(
            f"\nSe colocaron "
            f"{len(self.piezas_colocadas)} piezas en total. "
            f"¡Listo!"
        )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    assembler = PuzzleAssembler()

    assembler.armar_rompecabezas(
        id_rompecabezas="bus_001"
    )

    assembler.close()