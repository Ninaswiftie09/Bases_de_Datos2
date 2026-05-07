from typing import Any
from pydantic import BaseModel, Field


class NodeCreate(BaseModel):
    labels: list[str] = Field(..., min_length=1, examples=[["Usuario"], ["Usuario", "Sospechoso"]])
    properties: dict[str, Any] = Field(default_factory=dict)


class NodeUpdate(BaseModel):
    label: str
    match_property: str
    match_value: Any
    properties: dict[str, Any]


class NodePropertyDelete(BaseModel):
    label: str
    match_property: str
    match_value: Any
    property_names: list[str]


class NodeDelete(BaseModel):
    label: str
    match_property: str
    match_value: Any


class BulkNodeUpdate(BaseModel):
    label: str
    match_property: str | None = None
    match_value: Any | None = None
    properties: dict[str, Any]
    limit: int = 100


class BulkNodePropertyDelete(BaseModel):
    label: str
    match_property: str | None = None
    match_value: Any | None = None
    property_names: list[str]
    limit: int = 100


class BulkNodeDelete(BaseModel):
    label: str
    match_property: str | None = None
    match_value: Any | None = None
    limit: int = 100


class RelationshipCreate(BaseModel):
    from_label: str
    from_property: str
    from_value: Any
    to_label: str
    to_property: str
    to_value: Any
    relationship_type: str
    properties: dict[str, Any] = Field(default_factory=dict)


class RelationshipUpdate(BaseModel):
    element_id: str
    properties: dict[str, Any]


class RelationshipPropertyDelete(BaseModel):
    element_id: str
    property_names: list[str]


class RelationshipDelete(BaseModel):
    element_id: str


class BulkRelationshipUpdate(BaseModel):
    relationship_type: str
    match_property: str | None = None
    match_value: Any | None = None
    properties: dict[str, Any]
    limit: int = 100


class BulkRelationshipPropertyDelete(BaseModel):
    relationship_type: str
    match_property: str | None = None
    match_value: Any | None = None
    property_names: list[str]
    limit: int = 100


class BulkRelationshipDelete(BaseModel):
    relationship_type: str
    match_property: str | None = None
    match_value: Any | None = None
    limit: int = 100


class CsvUrlLoad(BaseModel):
    csv_url: str
    batch_size: int = 500
    clear_before_load: bool = False


class LocalCsvLoad(BaseModel):
    path: str = "../data/transacciones_fraude.csv"
    batch_size: int = 500
    clear_before_load: bool = False
