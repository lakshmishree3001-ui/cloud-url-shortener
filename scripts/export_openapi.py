"""
OpenAPI Specification Exporter.
Lab 14: Extracts and exports OpenAPI schema from FastAPI to docs/openapi.json.
"""
import io
import json
import os
import sys

# Ensure UTF-8 output even on Windows command prompt
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app


def export_openapi_schema(output_path: str = None):
    if output_path is None:
        output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "openapi.json"))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    schema = app.openapi()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    print(f"[OK] Successfully exported OpenAPI schema to: {output_path}")
    print(f"     API Title: {schema.get('info', {}).get('title')}")
    print(f"     Version:   {schema.get('info', {}).get('version')}")
    print(f"     Endpoints: {len(schema.get('paths', {}))} routes documented.")


if __name__ == "__main__":
    export_openapi_schema()
