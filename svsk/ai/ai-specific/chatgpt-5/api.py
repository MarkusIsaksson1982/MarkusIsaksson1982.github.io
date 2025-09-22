from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from curriculum_parser_v2 import CurriculumParserV2
import json
import networkx as nx
from typing import Dict

app = FastAPI(title="Gymnasium Assessment Toolkit API")
parser = CurriculumParserV2()

@app.post("/parse/pdf")
async def parse_pdf(file: UploadFile = File(...)):
    """
    Stub: accepts a PDF upload and (eventually) extracts structured curriculum data.
    Right now it just rejects because the PDF parser is not implemented.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # TODO: integrate skolverket_parser.py here
    raise HTTPException(status_code=501, detail="PDF parsing not yet implemented")

@app.get("/parse/manifest")
async def parse_manifest(path: str, validate: bool = True):
    """
    Parse a manifest.json or gy25_manifest.json file from disk.
    """
    try:
        result = parser.parse_file(path, validate=validate)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/bridges")
async def analyze_bridges(data: Dict):
    """
    Stub: analyze possible 'bridges' between curriculum elements using embeddings.
    Right now just echoes back the data structure.
    """
    # TODO: integrate embeddings + similarity search
    return {"message": "Bridge analysis not implemented yet", "input_size": len(data)}

@app.get("/visualize/graph")
async def visualize_graph(path: str):
    """
    Construct a curriculum/bridge network graph from a manifest or gy25 file.
    Returns nodes/edges suitable for frontend visualization.
    """
    try:
        result = parser.parse_file(path, validate=True)
        data = result["data"]
        fmt = result["format"]

        G = nx.Graph()

        if fmt == "gy25_curriculum":
            # Add programs
            for category, items in data["programs"].items():
                for program in items:
                    pname = program["name"] if isinstance(program, dict) else program
                    G.add_node(pname, type="program", category=category)

                    if isinstance(program, dict) and "inriktningar" in program:
                        for track in program["inriktningar"]:
                            G.add_node(track, type="inriktning", parent=pname)
                            G.add_edge(pname, track)

            # Add subjects
            for subj in data["subjects"]:
                G.add_node(subj, type="subject")

        elif fmt == "manifest":
            # Add repo structure as graph nodes
            def walk(node, parent=None):
                G.add_node(node["name"], type=node["type"])
                if parent:
                    G.add_edge(parent, node["name"])
                for child in node.get("children", []):
                    walk(child, node["name"])

            walk(data)

        # Convert graph to JSON for frontend
        nodes = [{"id": n, **G.nodes[n]} for n in G.nodes]
        edges = [{"source": u, "target": v} for u, v in G.edges]

        return {"nodes": nodes, "edges": edges}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
