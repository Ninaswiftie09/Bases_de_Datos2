from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.db import Neo4jConnection
from app.graph_service import GraphService


def main():
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "data" / "transacciones_fraude.csv"
    clear = "--clear" in sys.argv
    db = Neo4jConnection()
    service = GraphService(db)
    try:
        result = service.load_csv_file(csv_path, batch_size=500, clear_before_load=clear)
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
