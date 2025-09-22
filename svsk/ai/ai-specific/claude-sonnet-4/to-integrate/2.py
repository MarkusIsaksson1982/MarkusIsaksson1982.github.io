from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import Dict, List, Optional, Any
import json
import networkx as nx
import tempfile
import os
from datetime import datetime
import asyncio

# Import your enhanced curriculum parser
from curriculum_parser import CurriculumParser, CurriculumData

app = FastAPI(
    title="Gymnasium Assessment Toolkit API",
    description="API for Swedish curriculum parsing and analysis",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://markusisaksson1982.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize parser
parser = CurriculumParser(use_transformers=True)

# Request/Response Models
class ParseRequest(BaseModel):
    file_path: str
    validate: bool = True
    use_transformers: bool = True

class ManifestParseRequest(BaseModel):
    manifest_path: str
    max_concurrent: int = 3

class BridgeAnalysisRequest(BaseModel):
    descriptor: str
    language: str = "sv"
    threshold: float = 0.1

class GraphRequest(BaseModel):
    curriculum_data: Dict[str, Any]
    include_bridges: bool = True
    layout_algorithm: str = "spring"

class ExportRequest(BaseModel):
    curriculum_data: Dict[str, Any]
    format: str  # "markdown", "json", "csv"

# Response Models
class ParseResponse(BaseModel):
    success: bool
    curriculum_data: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    processing_time_ms: float
    error: Optional[str] = None

class BridgeAnalysisResponse(BaseModel):
    bridges: Dict[str, Dict[str, float]]
    descriptor: str
    language: str
    threshold_used: float

class GraphResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    layout: str
    metadata: Dict[str, Any]

# Endpoints
@app.get("/")
async def root():
    return {"message": "Gymnasium Assessment Toolkit API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "transformers_available": parser.use_transformers
    }

@app.post("/parse/pdf", response_model=ParseResponse)
async def parse_pdf(request: ParseRequest):
    """Parse a single PDF file or URL."""
    start_time = datetime.now()
    
    try:
        is_url = request.file_path.startswith(('http://', 'https://'))
        curriculum_data = parser.parse_pdf_with_validation(
            request.file_path, 
            is_url=is_url
        )
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return ParseResponse(
            success=True,
            curriculum_data=curriculum_data.__dict__ if hasattr(curriculum_data, '__dict__') 
                          else curriculum_data,
            metadata={
                "source": request.file_path,
                "is_url": is_url,
                "validation_enabled": request.validate,
                "subjects_found": len(curriculum_data.subjects)
            },
            processing_time_ms=processing_time
        )
    
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        return ParseResponse(
            success=False,
            curriculum_data=None,
            metadata={"source": request.file_path},
            processing_time_ms=processing_time,
            error=str(e)
        )

@app.post("/parse/manifest", response_model=List[ParseResponse])
async def parse_manifest(request: ManifestParseRequest):
    """Parse multiple PDFs from gy25_manifest.json."""
    try:
        results = parser.parse_manifest(request.manifest_path)
        
        responses = []
        for result in results:
            responses.append(ParseResponse(
                success=True,
                curriculum_data=result.__dict__ if hasattr(result, '__dict__') else result,
                metadata={
                    "source": "manifest_batch",
                    "subjects_found": len(result.subjects) if result else 0
                },
                processing_time_ms=0.0  # Not tracked for batch
            ))
        
        return responses
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/bridges", response_model=BridgeAnalysisResponse)
async def analyze_bridges(request: BridgeAnalysisRequest):
    """Generate bridge analysis for a competency descriptor."""
    try:
        bridges = parser.generate_bridges_embedding(
            request.descriptor,
            lang=request.language,
            threshold=request.threshold
        )
        
        return BridgeAnalysisResponse(
            bridges=bridges,
            descriptor=request.descriptor,
            language=request.language,
            threshold_used=request.threshold
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/visualize/graph", response_model=GraphResponse)
async def generate_graph(request: GraphRequest):
    """Generate network graph for visualization."""
    try:
        # Create NetworkX graph
        G = nx.DiGraph()
        
        curriculum_data = request.curriculum_data
        
        # Add subject nodes
        for subject in curriculum_data.get('subjects', []):
            subject_name = subject.get('subject_name', 'Unknown')
            G.add_node(subject_name, 
                      type='subject',
                      competency_count=len(subject.get('competencies', {})),
                      section_id=subject.get('section_id', ''))
        
        # Add bridge edges if requested
        if request.include_bridges:
            for subject in curriculum_data.get('subjects', []):
                subject_name = subject.get('subject_name', '')
                for comp_id, comp in subject.get('competencies', {}).items():
                    bridges = comp.get('bridges', {})
                    for target_subject, scores in bridges.items():
                        if target_subject in G.nodes:
                            weight = scores.get('norm', scores.get('raw', 0.1)) if isinstance(scores, dict) else scores
                            G.add_edge(subject_name, target_subject, 
                                     weight=weight, 
                                     competency=comp_id,
                                     descriptor=comp.get('descriptor', ''))
        
        # Generate layout
        if request.layout_algorithm == "spring":
            pos = nx.spring_layout(G, k=1, iterations=50)
        elif request.layout_algorithm == "circular":
            pos = nx.circular_layout(G)
        else:
            pos = nx.random_layout(G)
        
        # Convert to frontend format
        nodes = []
        for node, attrs in G.nodes(data=True):
            nodes.append({
                "id": node,
                "label": node,
                "x": pos[node][0] * 1000,  # Scale for frontend
                "y": pos[node][1] * 1000,
                **attrs
            })
        
        edges = []
        for source, target, attrs in G.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "weight": attrs.get('weight', 0.1),
                "competency": attrs.get('competency', ''),
                "descriptor": attrs.get('descriptor', '')[:100] + "..." if len(attrs.get('descriptor', '')) > 100 else attrs.get('descriptor', '')
            })
        
        return GraphResponse(
            nodes=nodes,
            edges=edges,
            layout=request.layout_algorithm,
            metadata={
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "connected_components": nx.number_weakly_connected_components(G)
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export/{format_type}")
async def export_data(format_type: str, request: ExportRequest):
    """Export curriculum data in various formats."""
    try:
        if format_type == "markdown":
            # Convert curriculum data to markdown
            content = generate_markdown_export(request.curriculum_data)
            return {"content": content, "format": "markdown"}
        
        elif format_type == "json":
            return {"content": json.dumps(request.curriculum_data, indent=2, ensure_ascii=False), "format": "json"}
        
        elif format_type == "csv":
            content = generate_csv_export(request.curriculum_data)
            return {"content": content, "format": "csv"}
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format_type}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and parse PDF file."""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Parse the uploaded file
        curriculum_data = parser.parse_pdf_with_validation(tmp_file_path, is_url=False)
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return {
            "success": True,
            "filename": file.filename,
            "curriculum_data": curriculum_data.__dict__ if hasattr(curriculum_data, '__dict__') else curriculum_data,
            "subjects_found": len(curriculum_data.subjects)
        }
    
    except Exception as e:
        # Clean up on error
        if 'tmp_file_path' in locals():
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def generate_markdown_export(curriculum_data: Dict) -> str:
    """Generate markdown export of curriculum data."""
    lines = ["# Curriculum Analysis Report\n"]
    
    metadata = curriculum_data.get('metadata', {})
    lines.append(f"**Source:** {metadata.get('source', 'Unknown')}")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    subjects = curriculum_data.get('subjects', [])
    for subject in subjects:
        lines.append(f"## {subject.get('subject_name', 'Unknown Subject')}")
        lines.append("")
        
        competencies = subject.get('competencies', {})
        if competencies:
            lines.append("### Competencies")
            for comp_id, comp in competencies.items():
                lines.append(f"- **{comp_id}:** {comp.get('descriptor', '')}")
                
                bridges = comp.get('bridges', {})
                if bridges:
                    lines.append("  - **Related subjects:**")
                    for bridge_subject, scores in bridges.items():
                        score = scores.get('norm', scores.get('raw', scores)) if isinstance(scores, dict) else scores
                        lines.append(f"    - {bridge_subject}: {score:.3f}")
                lines.append("")
    
    return "\n".join(lines)

def generate_csv_export(curriculum_data: Dict) -> str:
    """Generate CSV export of curriculum data."""
    lines = ["Subject,Competency ID,Descriptor,Keywords,Bridge Subject,Bridge Score"]
    
    subjects = curriculum_data.get('subjects', [])
    for subject in subjects:
        subject_name = subject.get('subject_name', '')
        competencies = subject.get('competencies', {})
        
        for comp_id, comp in competencies.items():
            descriptor = comp.get('descriptor', '').replace(',', ';')  # Escape commas
            keywords = ';'.join(comp.get('keywords', []))
            
            bridges = comp.get('bridges', {})
            if bridges:
                for bridge_subject, scores in bridges.items():
                    score = scores.get('norm', scores.get('raw', scores)) if isinstance(scores, dict) else scores
                    lines.append(f'"{subject_name}","{comp_id}","{descriptor}","{keywords}","{bridge_subject}",{score:.6f}')
            else:
                lines.append(f'"{subject_name}","{comp_id}","{descriptor}","{keywords}",,')
    
    return "\n".join(lines)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
