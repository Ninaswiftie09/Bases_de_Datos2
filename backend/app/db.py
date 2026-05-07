from neo4j import GraphDatabase
from .settings import get_settings


class Neo4jConnection:
    def __init__(self) -> None:
        settings = get_settings()
        self.database = settings.neo4j_database
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password),
        )

    def close(self) -> None:
        self.driver.close()

    def verify(self) -> bool:
        self.driver.verify_connectivity()
        return True

    def execute_read(self, query: str, parameters: dict | None = None):
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def execute_write(self, query: str, parameters: dict | None = None):
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
