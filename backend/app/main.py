from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .db import Neo4jConnection
from .graph_service import GraphService
from .schemas import (
    BulkNodeDelete,
    BulkNodePropertyDelete,
    BulkNodeUpdate,
    BulkRelationshipDelete,
    BulkRelationshipPropertyDelete,
    BulkRelationshipUpdate,
    CsvUrlLoad,
    LocalCsvLoad,
    NodeCreate,
    NodeDelete,
    NodePropertyDelete,
    NodeUpdate,
    RelationshipCreate,
    RelationshipDelete,
    RelationshipPropertyDelete,
    RelationshipUpdate,
)
from .settings import get_settings
DEFAULT_CSV_URL = "https://raw.githubusercontent.com/Ninaswiftie09/Bases_de_Datos2/refs/heads/Proyecto2/data/transacciones_fraude.csv"
settings = get_settings()
app = FastAPI(
    title="API de Detección de Fraude con Neo4j",
    description="Backend funcional para gestionar un grafo de fraude bancario en Neo4j/AuraDB.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connection = Neo4jConnection()
service = GraphService(connection)


def get_service() -> GraphService:
    return service


def handle_error(exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    raise HTTPException(status_code=500, detail=str(exc)) from exc

@app.post("/load/default")
async def load_default(
    batch_size: int = Query(500, ge=1, le=2000),
    clear_before_load: bool = Query(False),
    graph: GraphService = Depends(get_service),
):
    try:
        return await graph.load_csv_url(DEFAULT_CSV_URL, batch_size, clear_before_load)
    except Exception as exc:
        handle_error(exc)
        
@app.on_event("shutdown")
def shutdown_event():
    connection.close()


@app.get("/health")
def health(graph: GraphService = Depends(get_service)):
    try:
        return graph.health()
    except Exception as exc:
        handle_error(exc)


@app.post("/setup/constraints")
def setup_constraints(graph: GraphService = Depends(get_service)):
    try:
        return graph.create_constraints()
    except Exception as exc:
        handle_error(exc)


@app.delete("/setup/clear")
def clear_database(graph: GraphService = Depends(get_service)):
    try:
        return graph.clear_database()
    except Exception as exc:
        handle_error(exc)


@app.get("/summary")
def summary(graph: GraphService = Depends(get_service)):
    try:
        return graph.summary()
    except Exception as exc:
        handle_error(exc)


@app.post("/load/local")
def load_local(payload: LocalCsvLoad, graph: GraphService = Depends(get_service)):
    try:
        path = Path(payload.path)
        if not path.is_absolute():
            path = (Path.cwd() / path).resolve()
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"No existe el archivo: {path}")
        return graph.load_csv_file(path, payload.batch_size, payload.clear_before_load)
    except Exception as exc:
        handle_error(exc)


@app.post("/load/url")
async def load_url(payload: CsvUrlLoad, graph: GraphService = Depends(get_service)):
    try:
        return await graph.load_csv_url(payload.csv_url, payload.batch_size, payload.clear_before_load)
    except Exception as exc:
        handle_error(exc)


@app.post("/load/upload")
async def load_upload(
    file: UploadFile = File(...),
    batch_size: int = Query(500, ge=1, le=2000),
    clear_before_load: bool = Query(False),
    graph: GraphService = Depends(get_service),
):
    try:
        return await graph.load_upload(file, batch_size, clear_before_load)
    except Exception as exc:
        handle_error(exc)


@app.post("/nodes")
def create_node(payload: NodeCreate, graph: GraphService = Depends(get_service)):
    try:
        return graph.create_node(payload.labels, payload.properties)
    except Exception as exc:
        handle_error(exc)

@app.get("/nodes/by-id/{element_id}")
def get_node_by_id(element_id: str, graph: GraphService = Depends(get_service)):
    try:
        return graph.get_node_by_id(element_id)
    except Exception as exc:
        handle_error(exc)


@app.get("/nodes/aggregations/summary")
def node_aggregations(graph: GraphService = Depends(get_service)):
    try:
        return graph.node_aggregations()
    except Exception as exc:
        handle_error(exc)

@app.get("/nodes/{label}")
def get_nodes(
    label: str,
    match_property: str | None = None,
    match_value: str | None = None,
    limit: int = Query(50, ge=1, le=500),
    graph: GraphService = Depends(get_service),
):
    try:
        return graph.get_nodes(label, match_property, match_value, limit)
    except Exception as exc:
        handle_error(exc)


@app.patch("/nodes")
def update_node(payload: NodeUpdate, graph: GraphService = Depends(get_service)):
    try:
        return graph.update_node(payload.label, payload.match_property, payload.match_value, payload.properties)
    except Exception as exc:
        handle_error(exc)


@app.delete("/nodes/properties")
def delete_node_properties(payload: NodePropertyDelete, graph: GraphService = Depends(get_service)):
    try:
        return graph.delete_node_properties(payload.label, payload.match_property, payload.match_value, payload.property_names)
    except Exception as exc:
        handle_error(exc)


@app.delete("/nodes")
def delete_node(payload: NodeDelete, graph: GraphService = Depends(get_service)):
    try:
        return graph.delete_node(payload.label, payload.match_property, payload.match_value)
    except Exception as exc:
        handle_error(exc)


@app.patch("/nodes/bulk")
def bulk_update_nodes(payload: BulkNodeUpdate, graph: GraphService = Depends(get_service)):
    try:
        return graph.bulk_update_nodes(payload.label, payload.properties, payload.match_property, payload.match_value, payload.limit)
    except Exception as exc:
        handle_error(exc)


@app.delete("/nodes/bulk/properties")
def bulk_delete_node_properties(payload: BulkNodePropertyDelete, graph: GraphService = Depends(get_service)):
    try:
        return graph.bulk_delete_node_properties(payload.label, payload.property_names, payload.match_property, payload.match_value, payload.limit)
    except Exception as exc:
        handle_error(exc)


@app.delete("/nodes/bulk")
def bulk_delete_nodes(payload: BulkNodeDelete, graph: GraphService = Depends(get_service)):
    try:
        return graph.bulk_delete_nodes(payload.label, payload.match_property, payload.match_value, payload.limit)
    except Exception as exc:
        handle_error(exc)


@app.post("/relationships")
def create_relationship(payload: RelationshipCreate, graph: GraphService = Depends(get_service)):
    try:
        return graph.create_relationship(payload)
    except Exception as exc:
        handle_error(exc)


@app.get("/relationships")
def get_relationships(
    relationship_type: str | None = None,
    limit: int = Query(50, ge=1, le=500),
    graph: GraphService = Depends(get_service),
):
    try:
        return graph.get_relationships(relationship_type, limit)
    except Exception as exc:
        handle_error(exc)


@app.patch("/relationships")
def update_relationship(payload: RelationshipUpdate, graph: GraphService = Depends(get_service)):
    try:
        return graph.update_relationship(payload.element_id, payload.properties)
    except Exception as exc:
        handle_error(exc)


@app.delete("/relationships/properties")
def delete_relationship_properties(payload: RelationshipPropertyDelete, graph: GraphService = Depends(get_service)):
    try:
        return graph.delete_relationship_properties(payload.element_id, payload.property_names)
    except Exception as exc:
        handle_error(exc)


@app.delete("/relationships")
def delete_relationship(payload: RelationshipDelete, graph: GraphService = Depends(get_service)):
    try:
        return graph.delete_relationship(payload.element_id)
    except Exception as exc:
        handle_error(exc)


@app.patch("/relationships/bulk")
def bulk_update_relationships(payload: BulkRelationshipUpdate, graph: GraphService = Depends(get_service)):
    try:
        return graph.bulk_update_relationships(payload.relationship_type, payload.properties, payload.match_property, payload.match_value, payload.limit)
    except Exception as exc:
        handle_error(exc)


@app.delete("/relationships/bulk/properties")
def bulk_delete_relationship_properties(payload: BulkRelationshipPropertyDelete, graph: GraphService = Depends(get_service)):
    try:
        return graph.bulk_delete_relationship_properties(payload.relationship_type, payload.property_names, payload.match_property, payload.match_value, payload.limit)
    except Exception as exc:
        handle_error(exc)


@app.delete("/relationships/bulk")
def bulk_delete_relationships(payload: BulkRelationshipDelete, graph: GraphService = Depends(get_service)):
    try:
        return graph.bulk_delete_relationships(payload.relationship_type, payload.match_property, payload.match_value, payload.limit)
    except Exception as exc:
        handle_error(exc)


@app.get("/graph/sample")
def graph_sample(limit: int = Query(120, ge=1, le=500), graph: GraphService = Depends(get_service)):
    try:
        return graph.graph_sample(limit)
    except Exception as exc:
        handle_error(exc)


@app.get("/queries/{query_name}")
def run_query(query_name: str, limit: int = Query(50, ge=1, le=500), graph: GraphService = Depends(get_service)):
    try:
        return graph.cypher_query(query_name, limit)
    except Exception as exc:
        handle_error(exc)


@app.get("/fraud/score")
def fraud_score(limit: int = Query(50, ge=1, le=500), graph: GraphService = Depends(get_service)):
    try:
        return graph.fraud_score(limit)
    except Exception as exc:
        handle_error(exc)

@app.get("/graph/connected")
def graph_connected(graph: GraphService = Depends(get_service)):
    try:
        return graph.is_graph_connected()
    except Exception as exc:
        handle_error(exc)