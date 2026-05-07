from __future__ import annotations

import csv
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

import httpx
from fastapi import HTTPException, UploadFile
from neo4j.time import Date, DateTime, Time

from .db import Neo4jConnection
from .utils import cypher_label, cypher_type, normalize_properties, parse_bool, split_list, validate_name


class GraphService:
    def __init__(self, db: Neo4jConnection) -> None:
        self.db = db

    @staticmethod
    def serialize(value: Any) -> Any:
        if isinstance(value, (Date, DateTime, Time)):
            return value.iso_format()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, list):
            return [GraphService.serialize(v) for v in value]
        if isinstance(value, dict):
            return {k: GraphService.serialize(v) for k, v in value.items()}
        return value

    def _run_read(self, query: str, parameters: dict | None = None):
        return self.serialize(self.db.execute_read(query, parameters))

    def _run_write(self, query: str, parameters: dict | None = None):
        return self.serialize(self.db.execute_write(query, parameters))

    def create_constraints(self) -> dict[str, Any]:
        statements = [
            "CREATE CONSTRAINT usuario_id IF NOT EXISTS FOR (n:Usuario) REQUIRE n.id_usuario IS UNIQUE",
            "CREATE CONSTRAINT cuenta_id IF NOT EXISTS FOR (n:Cuenta) REQUIRE n.id_cuenta IS UNIQUE",
            "CREATE CONSTRAINT transaccion_id IF NOT EXISTS FOR (n:Transaccion) REQUIRE n.id_transaccion IS UNIQUE",
            "CREATE CONSTRAINT dispositivo_id IF NOT EXISTS FOR (n:Dispositivo) REQUIRE n.id_dispositivo IS UNIQUE",
            "CREATE CONSTRAINT ubicacion_id IF NOT EXISTS FOR (n:Ubicacion) REQUIRE n.id_ubicacion IS UNIQUE",
            "CREATE INDEX usuario_nombre IF NOT EXISTS FOR (n:Usuario) ON (n.nombre)",
            "CREATE INDEX cuenta_riesgo IF NOT EXISTS FOR (n:Cuenta) ON (n.nivel_riesgo)",
            "CREATE INDEX transaccion_monto IF NOT EXISTS FOR (n:Transaccion) ON (n.monto)",
            "CREATE INDEX transaccion_fecha IF NOT EXISTS FOR (n:Transaccion) ON (n.fecha)",
            "CREATE INDEX dispositivo_confiable IF NOT EXISTS FOR (n:Dispositivo) ON (n.confiable)",
        ]
        for stmt in statements:
            self._run_write(stmt)
        return {"message": "Constraints e índices creados o verificados", "total": len(statements)}

    def clear_database(self) -> dict[str, str]:
        self._run_write("MATCH (n) DETACH DELETE n")
        return {"message": "Base de datos limpiada correctamente"}

    def health(self) -> dict[str, Any]:
        self.db.verify()
        info = self._run_read("RETURN 'Neo4j conectado' AS status, datetime() AS checked_at")
        return info[0]

    def summary(self) -> dict[str, Any]:
        labels = self._run_read(
            """
            CALL db.labels() YIELD label
            CALL {
              WITH label
              MATCH (n)
              WHERE label IN labels(n)
              RETURN count(n) AS total
            }
            RETURN label, total
            ORDER BY label
            """
        )
        relationships = self._run_read(
            """
            CALL db.relationshipTypes() YIELD relationshipType
            CALL {
              WITH relationshipType
              MATCH ()-[r]->()
              WHERE type(r) = relationshipType
              RETURN count(r) AS total
            }
            RETURN relationshipType, total
            ORDER BY relationshipType
            """
        )
        totals = self._run_read(
            """
            CALL { MATCH (n) RETURN count(n) AS total_nodes }
            CALL { MATCH ()-[r]->() RETURN count(r) AS total_relationships }
            CALL { MATCH (t:Transaccion {es_sospechosa: true}) RETURN count(t) AS suspicious_transactions }
            RETURN total_nodes, total_relationships, suspicious_transactions
            """
        )[0]
        return {"totals": totals, "labels": labels, "relationships": relationships}

    @staticmethod
    def _convert_row(row: dict[str, str]) -> dict[str, Any]:
        converted: dict[str, Any] = {}
        integer_fields = {"usuario_edad", "transaccion_minuto_dia", "transaccion_riesgo_score"}
        float_tokens = ("saldo", "monto", "latitud", "longitud")
        bool_tokens = ("verificado", "activa", "confiable", "zona_riesgo", "es_sospechosa")
        date_tokens = ("fecha", "ultimo_uso")
        list_fields = {"usuario_correos_asociados", "transaccion_etiquetas_alerta"}
        for key, value in row.items():
            raw = value.strip() if isinstance(value, str) else value
            if raw == "":
                converted[key] = None
            elif key in integer_fields:
                converted[key] = int(float(raw))
            elif any(token in key for token in float_tokens):
                converted[key] = float(raw)
            elif any(token in key for token in bool_tokens):
                converted[key] = parse_bool(raw)
            elif key in list_fields:
                converted[key] = split_list(raw)
            elif any(token in key for token in date_tokens):
                converted[key] = date.fromisoformat(str(raw))
            else:
                converted[key] = raw
        return converted

    def _load_rows(self, rows: list[dict[str, Any]], batch_size: int) -> dict[str, Any]:
        self.create_constraints()
        query = """
        UNWIND $rows AS row
        MERGE (u:Usuario {id_usuario: row.usuario_id})
        SET u.nombre = row.usuario_nombre,
            u.edad = row.usuario_edad,
            u.verificado = row.usuario_verificado,
            u.correos_asociados = row.usuario_correos_asociados,
            u.fecha_registro = row.usuario_fecha_registro

        MERGE (co:Cuenta {id_cuenta: row.cuenta_origen_id})
        SET co.saldo = row.cuenta_origen_saldo,
            co.tipo = row.cuenta_origen_tipo,
            co.fecha_creacion = row.cuenta_origen_fecha_creacion,
            co.activa = row.cuenta_origen_activa,
            co.nivel_riesgo = row.cuenta_origen_nivel_riesgo

        MERGE (cd:Cuenta {id_cuenta: row.cuenta_destino_id})
        SET cd.saldo = row.cuenta_destino_saldo,
            cd.tipo = row.cuenta_destino_tipo,
            cd.fecha_creacion = row.cuenta_destino_fecha_creacion,
            cd.activa = row.cuenta_destino_activa,
            cd.nivel_riesgo = row.cuenta_destino_nivel_riesgo

        MERGE (t:Transaccion {id_transaccion: row.transaccion_id})
        SET t.monto = row.transaccion_monto,
            t.fecha = row.transaccion_fecha,
            t.minuto_dia = row.transaccion_minuto_dia,
            t.tipo = row.transaccion_tipo,
            t.canal = row.transaccion_canal,
            t.etiquetas_alerta = row.transaccion_etiquetas_alerta,
            t.es_sospechosa = row.transaccion_es_sospechosa,
            t.riesgo_score = row.transaccion_riesgo_score

        MERGE (d:Dispositivo {id_dispositivo: row.dispositivo_id})
        SET d.tipo = row.dispositivo_tipo,
            d.ip = row.dispositivo_ip,
            d.sistema_operativo = row.dispositivo_sistema_operativo,
            d.confiable = row.dispositivo_confiable,
            d.ultimo_uso = row.dispositivo_ultimo_uso

        MERGE (ur:Ubicacion {id_ubicacion: row.ubicacion_residencia_id})
        SET ur.pais = row.ubicacion_residencia_pais,
            ur.ciudad = row.ubicacion_residencia_ciudad,
            ur.latitud = row.ubicacion_residencia_latitud,
            ur.longitud = row.ubicacion_residencia_longitud,
            ur.zona_riesgo = row.ubicacion_residencia_zona_riesgo

        MERGE (ut:Ubicacion {id_ubicacion: row.ubicacion_transaccion_id})
        SET ut.pais = row.ubicacion_transaccion_pais,
            ut.ciudad = row.ubicacion_transaccion_ciudad,
            ut.latitud = row.ubicacion_transaccion_latitud,
            ut.longitud = row.ubicacion_transaccion_longitud,
            ut.zona_riesgo = row.ubicacion_transaccion_zona_riesgo

        MERGE (uc:Ubicacion {id_ubicacion: row.ubicacion_cuenta_id})
        SET uc.pais = row.ubicacion_cuenta_pais,
            uc.ciudad = row.ubicacion_cuenta_ciudad,
            uc.latitud = row.ubicacion_cuenta_latitud,
            uc.longitud = row.ubicacion_cuenta_longitud,
            uc.zona_riesgo = row.ubicacion_cuenta_zona_riesgo

        MERGE (ud:Ubicacion {id_ubicacion: row.ubicacion_dispositivo_id})
        SET ud.pais = row.ubicacion_dispositivo_pais,
            ud.ciudad = row.ubicacion_dispositivo_ciudad,
            ud.latitud = row.ubicacion_dispositivo_latitud,
            ud.longitud = row.ubicacion_dispositivo_longitud,
            ud.zona_riesgo = row.ubicacion_dispositivo_zona_riesgo

        MERGE (u)-[r1:TIENE_CUENTA]->(co)
        SET r1.fecha_creacion = row.cuenta_origen_fecha_creacion, r1.fuente = 'csv', r1.confianza = 0.98, r1.rol = 'titular', r1.activa = row.cuenta_origen_activa

        MERGE (co)-[r2:EMITE]->(t)
        SET r2.fecha_creacion = row.transaccion_fecha, r2.fuente = 'csv', r2.confianza = 0.97, r2.canal = row.transaccion_canal, r2.estado = 'procesada', r2.monto_referencia = row.transaccion_monto

        MERGE (t)-[r3:TRANSFIERE_A]->(cd)
        SET r3.fecha_creacion = row.transaccion_fecha, r3.fuente = 'csv', r3.confianza = 0.96, r3.canal = row.transaccion_canal, r3.resultado = 'aprobada', r3.riesgo_relacion = row.transaccion_riesgo_score

        MERGE (u)-[r4:USA]->(d)
        SET r4.fecha_creacion = row.usuario_fecha_registro, r4.fuente = 'csv', r4.confianza = CASE WHEN row.dispositivo_confiable THEN 0.92 ELSE 0.45 END, r4.frecuencia_uso = 1, r4.verificado = row.dispositivo_confiable, r4.ultimo_uso = row.dispositivo_ultimo_uso

        MERGE (u)-[r5:RESIDE_EN]->(ur)
        SET r5.fecha_creacion = row.usuario_fecha_registro, r5.fuente = 'csv', r5.confianza = 0.9, r5.tipo_domicilio = 'principal', r5.confirmado = true

        MERGE (t)-[r6:SE_REALIZA_DESDE]->(d)
        SET r6.fecha_creacion = row.transaccion_fecha, r6.fuente = 'csv', r6.confianza = CASE WHEN row.dispositivo_confiable THEN 0.9 ELSE 0.4 END, r6.canal = row.transaccion_canal, r6.autenticacion = CASE WHEN row.dispositivo_confiable THEN 'normal' ELSE 'debil' END, r6.riesgo = row.transaccion_riesgo_score

        MERGE (t)-[r7:OCURRE_EN]->(ut)
        SET r7.fecha_creacion = row.transaccion_fecha, r7.fuente = 'csv', r7.confianza = 0.88, r7.zona_horaria = 'America/Guatemala', r7.gps_confirmado = true, r7.tipo_evento = row.transaccion_tipo

        MERGE (co)-[r8:REGISTRADA_EN]->(uc)
        SET r8.fecha_creacion = row.cuenta_origen_fecha_creacion, r8.fuente = 'csv', r8.confianza = 0.94, r8.sucursal = row.ubicacion_cuenta_ciudad, r8.verificada = true

        MERGE (co)-[r9:ASOCIADA_A]->(d)
        SET r9.fecha_creacion = row.cuenta_origen_fecha_creacion, r9.fuente = 'csv', r9.confianza = CASE WHEN row.dispositivo_confiable THEN 0.91 ELSE 0.5 END, r9.primer_uso = row.cuenta_origen_fecha_creacion, r9.activo = row.cuenta_origen_activa

        MERGE (d)-[r10:UBICADO_EN]->(ud)
        SET r10.fecha_creacion = row.dispositivo_ultimo_uso, r10.fuente = 'csv', r10.confianza = 0.85, r10.precision_gps = 25.0, r10.actualizado_en = row.dispositivo_ultimo_uso
        """
        loaded = 0
        for start in range(0, len(rows), batch_size):
            batch = rows[start : start + batch_size]
            self._run_write(query, {"rows": batch})
            loaded += len(batch)
        return {"message": "Carga CSV completada", "rows_loaded": loaded, "summary": self.summary()}

    def load_csv_file(self, file_path: Path, batch_size: int = 500, clear_before_load: bool = False) -> dict[str, Any]:
        if clear_before_load:
            self.clear_database()
        with file_path.open("r", encoding="utf-8-sig", newline="") as f:
            rows = [self._convert_row(row) for row in csv.DictReader(f)]
        return self._load_rows(rows, batch_size)

    async def load_upload(self, upload: UploadFile, batch_size: int = 500, clear_before_load: bool = False) -> dict[str, Any]:
        suffix = Path(upload.filename or "data.csv").suffix or ".csv"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await upload.read())
            tmp_path = Path(tmp.name)
        try:
            return self.load_csv_file(tmp_path, batch_size, clear_before_load)
        finally:
            tmp_path.unlink(missing_ok=True)

    async def load_csv_url(self, csv_url: str, batch_size: int = 500, clear_before_load: bool = False) -> dict[str, Any]:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp_path = Path(tmp.name)
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.get(csv_url)
                response.raise_for_status()
                tmp_path.write_bytes(response.content)
            return self.load_csv_file(tmp_path, batch_size, clear_before_load)
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=400, detail=f"No se pudo descargar el CSV: {exc}") from exc
        finally:
            tmp_path.unlink(missing_ok=True)

    def create_node(self, labels: list[str], properties: dict[str, Any]) -> dict[str, Any]:
        labels_cypher = ":".join(cypher_label(label) for label in labels)
        props = normalize_properties(properties)
        result = self._run_write(
            f"CREATE (n:{labels_cypher}) SET n = $properties RETURN elementId(n) AS element_id, labels(n) AS labels, properties(n) AS properties",
            {"properties": props},
        )
        return result[0]

    def get_node_by_id(self, element_id: str):
        result = self._run_read(
            """
            MATCH (n)
            WHERE elementId(n) = $element_id
            RETURN elementId(n) AS element_id,
                labels(n) AS labels,
                properties(n) AS properties
            """,
            {"element_id": element_id},
        )

        if not result:
            raise HTTPException(status_code=404, detail="No se encontró un nodo con ese element_id.")

        return result[0]


    def node_aggregations(self):
        nodes_by_label = self._run_read(
            """
            MATCH (n)
            UNWIND labels(n) AS label
            RETURN label, count(n) AS cantidad
            ORDER BY cantidad DESC
            """,
            {},
        )

        avg_amount_by_transaction_type = self._run_read(
            """
            MATCH (t:Transaccion)
            RETURN coalesce(t.tipo, 'Sin tipo') AS tipo_transaccion,
                round(avg(toFloat(t.monto)) * 100) / 100 AS promedio_monto,
                count(t) AS cantidad_transacciones
            ORDER BY promedio_monto DESC
            """,
            {},
        )

        suspicious_transactions_by_city = self._run_read(
            """
            MATCH (t:Transaccion)-[:OCURRE_EN]->(u:Ubicacion)
            WHERE coalesce(t.es_sospechosa, false) = true
            RETURN coalesce(u.ciudad, 'Sin ciudad') AS ciudad,
                count(t) AS total_sospechosas
            ORDER BY total_sospechosas DESC, ciudad ASC
            LIMIT 25
            """,
            {},
        )

        return {
            "nodes_by_label": nodes_by_label,
            "avg_amount_by_transaction_type": avg_amount_by_transaction_type,
            "suspicious_transactions_by_city": suspicious_transactions_by_city,
        }
    def get_nodes(self, label: str, match_property: str | None = None, match_value: Any | None = None, limit: int = 50):
        label_cypher = cypher_label(label)
        params: dict[str, Any] = {"limit": limit}
        where = ""
        if match_property and match_value is not None:
            validate_name(match_property, "propiedad")
            where = f"WHERE n.`{match_property}` = $match_value"
            params["match_value"] = normalize_properties({match_property: match_value})[match_property]
        return self._run_read(
            f"MATCH (n:{label_cypher}) {where} RETURN elementId(n) AS element_id, labels(n) AS labels, properties(n) AS properties LIMIT $limit",
            params,
        )

    def update_node(self, label: str, match_property: str, match_value: Any, properties: dict[str, Any]):
        label_cypher = cypher_label(label)
        validate_name(match_property, "propiedad")
        props = normalize_properties(properties)
        result = self._run_write(
            f"MATCH (n:{label_cypher}) WHERE n.`{match_property}` = $match_value SET n += $properties RETURN elementId(n) AS element_id, labels(n) AS labels, properties(n) AS properties",
            {"match_value": normalize_properties({match_property: match_value})[match_property], "properties": props},
        )
        return result

    def delete_node_properties(self, label: str, match_property: str, match_value: Any, property_names: list[str]):
        label_cypher = cypher_label(label)
        validate_name(match_property, "propiedad")
        remove_clause = ", ".join(f"n.`{validate_name(prop, 'propiedad')}`" for prop in property_names)
        result = self._run_write(
            f"MATCH (n:{label_cypher}) WHERE n.`{match_property}` = $match_value REMOVE {remove_clause} RETURN elementId(n) AS element_id, labels(n) AS labels, properties(n) AS properties",
            {"match_value": normalize_properties({match_property: match_value})[match_property]},
        )
        return result

    def delete_node(self, label: str, match_property: str, match_value: Any):
        label_cypher = cypher_label(label)
        validate_name(match_property, "propiedad")
        result = self._run_write(
            f"MATCH (n:{label_cypher}) WHERE n.`{match_property}` = $match_value WITH n, elementId(n) AS element_id DETACH DELETE n RETURN element_id",
            {"match_value": normalize_properties({match_property: match_value})[match_property]},
        )
        return {"deleted": len(result), "items": result}

    def bulk_update_nodes(self, label: str, properties: dict[str, Any], match_property: str | None = None, match_value: Any | None = None, limit: int = 100):
        label_cypher = cypher_label(label)
        props = normalize_properties(properties)
        params = {"properties": props, "limit": limit}
        where = ""
        if match_property and match_value is not None:
            validate_name(match_property, "propiedad")
            where = f"WHERE n.`{match_property}` = $match_value"
            params["match_value"] = normalize_properties({match_property: match_value})[match_property]
        result = self._run_write(
            f"MATCH (n:{label_cypher}) {where} WITH n LIMIT $limit SET n += $properties RETURN count(n) AS updated",
            params,
        )
        return result[0]

    def bulk_delete_node_properties(self, label: str, property_names: list[str], match_property: str | None = None, match_value: Any | None = None, limit: int = 100):
        label_cypher = cypher_label(label)
        remove_clause = ", ".join(f"n.`{validate_name(prop, 'propiedad')}`" for prop in property_names)
        params = {"limit": limit}
        where = ""
        if match_property and match_value is not None:
            validate_name(match_property, "propiedad")
            where = f"WHERE n.`{match_property}` = $match_value"
            params["match_value"] = normalize_properties({match_property: match_value})[match_property]
        result = self._run_write(
            f"MATCH (n:{label_cypher}) {where} WITH n LIMIT $limit REMOVE {remove_clause} RETURN count(n) AS updated",
            params,
        )
        return result[0]

    def bulk_delete_nodes(self, label: str, match_property: str | None = None, match_value: Any | None = None, limit: int = 100):
        label_cypher = cypher_label(label)
        params = {"limit": limit}
        where = ""
        if match_property and match_value is not None:
            validate_name(match_property, "propiedad")
            where = f"WHERE n.`{match_property}` = $match_value"
            params["match_value"] = normalize_properties({match_property: match_value})[match_property]
        result = self._run_write(
            f"MATCH (n:{label_cypher}) {where} WITH n LIMIT $limit DETACH DELETE n RETURN count(n) AS deleted",
            params,
        )
        return result[0]

    def create_relationship(self, payload) -> dict[str, Any]:
        from_label = cypher_label(payload.from_label)
        to_label = cypher_label(payload.to_label)
        rel_type = cypher_type(payload.relationship_type)
        validate_name(payload.from_property, "propiedad origen")
        validate_name(payload.to_property, "propiedad destino")
        props = normalize_properties(payload.properties)
        result = self._run_write(
            f"""
            MATCH (a:{from_label}) WHERE a.`{payload.from_property}` = $from_value
            MATCH (b:{to_label}) WHERE b.`{payload.to_property}` = $to_value
            CREATE (a)-[r:{rel_type}]->(b)
            SET r = $properties
            RETURN elementId(r) AS element_id, type(r) AS type, properties(r) AS properties,
                   elementId(a) AS from_element_id, labels(a) AS from_labels,
                   elementId(b) AS to_element_id, labels(b) AS to_labels
            """,
            {
                "from_value": normalize_properties({payload.from_property: payload.from_value})[payload.from_property],
                "to_value": normalize_properties({payload.to_property: payload.to_value})[payload.to_property],
                "properties": props,
            },
        )
        return result[0] if result else {"message": "No se encontraron nodos origen/destino"}

    def get_relationships(self, relationship_type: str | None = None, limit: int = 50):
        params = {"limit": limit}
        type_filter = ""
        if relationship_type:
            rel_type = validate_name(relationship_type, "tipo de relación")
            type_filter = f"WHERE type(r) = '{rel_type}'"
        return self._run_read(
            f"""
            MATCH (a)-[r]->(b)
            {type_filter}
            RETURN elementId(r) AS element_id, type(r) AS type, properties(r) AS properties,
                   elementId(a) AS from_element_id, labels(a) AS from_labels, properties(a) AS from_properties,
                   elementId(b) AS to_element_id, labels(b) AS to_labels, properties(b) AS to_properties
            LIMIT $limit
            """,
            params,
        )

    def update_relationship(self, element_id: str, properties: dict[str, Any]):
        props = normalize_properties(properties)
        result = self._run_write(
            "MATCH ()-[r]->() WHERE elementId(r) = $element_id SET r += $properties RETURN elementId(r) AS element_id, type(r) AS type, properties(r) AS properties",
            {"element_id": element_id, "properties": props},
        )
        return result

    def delete_relationship_properties(self, element_id: str, property_names: list[str]):
        remove_clause = ", ".join(f"r.`{validate_name(prop, 'propiedad')}`" for prop in property_names)
        result = self._run_write(
            f"MATCH ()-[r]->() WHERE elementId(r) = $element_id REMOVE {remove_clause} RETURN elementId(r) AS element_id, type(r) AS type, properties(r) AS properties",
            {"element_id": element_id},
        )
        return result

    def delete_relationship(self, element_id: str):
        result = self._run_write(
            "MATCH ()-[r]->() WHERE elementId(r) = $element_id WITH r, elementId(r) AS element_id DELETE r RETURN element_id",
            {"element_id": element_id},
        )
        return {"deleted": len(result), "items": result}

    def bulk_update_relationships(self, relationship_type: str, properties: dict[str, Any], match_property: str | None = None, match_value: Any | None = None, limit: int = 100):
        rel_type = cypher_type(relationship_type)
        params = {"properties": normalize_properties(properties), "limit": limit}
        where = ""
        if match_property and match_value is not None:
            validate_name(match_property, "propiedad")
            where = f"WHERE r.`{match_property}` = $match_value"
            params["match_value"] = normalize_properties({match_property: match_value})[match_property]
        result = self._run_write(
            f"MATCH ()-[r:{rel_type}]->() {where} WITH r LIMIT $limit SET r += $properties RETURN count(r) AS updated",
            params,
        )
        return result[0]

    def bulk_delete_relationship_properties(self, relationship_type: str, property_names: list[str], match_property: str | None = None, match_value: Any | None = None, limit: int = 100):
        rel_type = cypher_type(relationship_type)
        remove_clause = ", ".join(f"r.`{validate_name(prop, 'propiedad')}`" for prop in property_names)
        params = {"limit": limit}
        where = ""
        if match_property and match_value is not None:
            validate_name(match_property, "propiedad")
            where = f"WHERE r.`{match_property}` = $match_value"
            params["match_value"] = normalize_properties({match_property: match_value})[match_property]
        result = self._run_write(
            f"MATCH ()-[r:{rel_type}]->() {where} WITH r LIMIT $limit REMOVE {remove_clause} RETURN count(r) AS updated",
            params,
        )
        return result[0]

    def bulk_delete_relationships(self, relationship_type: str, match_property: str | None = None, match_value: Any | None = None, limit: int = 100):
        rel_type = cypher_type(relationship_type)
        params = {"limit": limit}
        where = ""
        if match_property and match_value is not None:
            validate_name(match_property, "propiedad")
            where = f"WHERE r.`{match_property}` = $match_value"
            params["match_value"] = normalize_properties({match_property: match_value})[match_property]
        result = self._run_write(
            f"MATCH ()-[r:{rel_type}]->() {where} WITH r LIMIT $limit DELETE r RETURN count(r) AS deleted",
            params,
        )
        return result[0]

    def graph_sample(self, limit: int = 120) -> dict[str, Any]:
        records = self._run_read(
            """
            MATCH (a)-[r]->(b)
            RETURN elementId(a) AS source, labels(a)[0] AS source_label, properties(a) AS source_props,
                   elementId(b) AS target, labels(b)[0] AS target_label, properties(b) AS target_props,
                   elementId(r) AS rel_id, type(r) AS type, properties(r) AS rel_props
            LIMIT $limit
            """,
            {"limit": limit},
        )
        node_map: dict[str, dict[str, Any]] = {}
        links = []
        for row in records:
            node_map[row["source"]] = {"id": row["source"], "label": row["source_label"], "properties": row["source_props"]}
            node_map[row["target"]] = {"id": row["target"], "label": row["target_label"], "properties": row["target_props"]}
            links.append({"source": row["source"], "target": row["target"], "type": row["type"], "id": row["rel_id"], "properties": row["rel_props"]})
        return {"nodes": list(node_map.values()), "links": links}

    def cypher_query(self, name: str, limit: int = 50):
        queries = {
            "small-frequent": """
                MATCH (c:Cuenta)-[:EMITE]->(t:Transaccion)
                WHERE t.monto < 100
                WITH c, t.fecha AS dia, count(t) AS cantidad, sum(t.monto) AS total, collect(t.id_transaccion)[0..10] AS transacciones
                WHERE cantidad >= 8
                RETURN c.id_cuenta AS cuenta, dia, cantidad, round(total, 2) AS total, transacciones
                ORDER BY cantidad DESC
                LIMIT $limit
            """,
            "shared-devices": """
                MATCH (u1:Usuario)-[:USA]->(d:Dispositivo)<-[:USA]-(u2:Usuario)
                WHERE u1.id_usuario < u2.id_usuario
                WITH d, collect(DISTINCT u1.nombre) + collect(DISTINCT u2.nombre) AS usuarios
                RETURN d.id_dispositivo AS dispositivo, size(apoc.coll.toSet(usuarios)) AS total_usuarios, apoc.coll.toSet(usuarios)[0..10] AS usuarios
                ORDER BY total_usuarios DESC
                LIMIT $limit
            """,
            "shared-devices-no-apoc": """
                MATCH (u:Usuario)-[:USA]->(d:Dispositivo)
                WITH d, collect(DISTINCT u.nombre) AS usuarios
                WHERE size(usuarios) >= 2
                RETURN d.id_dispositivo AS dispositivo, size(usuarios) AS total_usuarios, usuarios[0..10] AS usuarios
                ORDER BY total_usuarios DESC
                LIMIT $limit
            """,
            "unusual-locations": """
                MATCH (u:Usuario)-[:RESIDE_EN]->(ur:Ubicacion),
                      (u)-[:TIENE_CUENTA]->(c:Cuenta)-[:EMITE]->(t:Transaccion)-[:OCURRE_EN]->(ut:Ubicacion)
                WHERE ur.pais <> ut.pais OR ur.ciudad <> ut.ciudad
                RETURN u.nombre AS usuario, c.id_cuenta AS cuenta, t.id_transaccion AS transaccion,
                       ur.ciudad AS ciudad_residencia, ut.ciudad AS ciudad_transaccion, ut.pais AS pais_transaccion
                LIMIT $limit
            """,
            "high-amount": """
                MATCH (u:Usuario)-[:TIENE_CUENTA]->(c:Cuenta)-[:EMITE]->(t:Transaccion)
                WHERE t.monto > 10000
                RETURN u.nombre AS usuario, c.id_cuenta AS cuenta, t.id_transaccion AS transaccion, t.monto AS monto, t.fecha AS fecha
                ORDER BY monto DESC
                LIMIT $limit
            """,
            "new-or-inactive-accounts": """
                MATCH (t:Transaccion)-[:TRANSFIERE_A]->(c:Cuenta)
                WHERE c.activa = false OR c.fecha_creacion >= date('2026-03-01')
                WITH c, count(t) AS recibidas, sum(t.monto) AS total
                WHERE recibidas >= 3
                RETURN c.id_cuenta AS cuenta, c.activa AS activa, c.fecha_creacion AS fecha_creacion, recibidas, round(total, 2) AS total
                ORDER BY recibidas DESC
                LIMIT $limit
            """,
            "transfer-chains": """
                MATCH path = (c1:Cuenta)-[:EMITE]->(:Transaccion)-[:TRANSFIERE_A]->(c2:Cuenta)<-[:TRANSFIERE_A]-(:Transaccion)<-[:EMITE]-(c3:Cuenta)
                WHERE c1.id_cuenta <> c3.id_cuenta
                RETURN c1.id_cuenta AS cuenta_origen, c2.id_cuenta AS cuenta_intermedia, c3.id_cuenta AS cuenta_relacionada, length(path) AS profundidad
                LIMIT $limit
            """,
        }
        if name not in queries:
            raise HTTPException(status_code=404, detail="Consulta no encontrada")
        # Use no-apoc query by default for Aura free instances without APOC.
        if name == "shared-devices":
            name = "shared-devices-no-apoc"
        return self._run_read(queries[name], {"limit": limit})

    def fraud_score(self, limit: int = 50):
        return self._run_read(
            """
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
            RETURN u.id_usuario AS id_usuario, u.nombre AS usuario, c.id_cuenta AS cuenta, score,
                   micro_count, dispositivos_no_confiables, dispositivos_compartidos, cuentas_destino_riesgo,
                   CASE WHEN score >= 70 THEN 'alto' WHEN score >= 40 THEN 'medio' ELSE 'bajo' END AS nivel_riesgo
            ORDER BY score DESC
            LIMIT $limit
            """,
            {"limit": limit},
        )
    
    def is_graph_connected(self):
        result = self._run_read("""
            MATCH (n)
            WITH collect(n) AS nodes
            CALL {
                WITH nodes
                MATCH (start)
                WITH start
                MATCH (start)-[*]-(reachable)
                RETURN count(DISTINCT reachable) AS reachable_count
                LIMIT 1
            }
            RETURN size(nodes) AS total_nodes, reachable_count
        """)

        if not result:
            return {"total_nodes": 0, "reachable": 0, "is_connected": False}

        data = result[0]
        total = data["total_nodes"]
        reachable = data["reachable_count"]

        return {
            "total_nodes": total,
            "reachable_nodes": reachable,
            "is_connected": total == reachable
        }
    
    
