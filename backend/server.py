from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from controller import BugIntelligenceController
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Bug Intelligence System API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize multi-agent system
print("🚀 Initializing Multi-Agent System...")

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_dir = os.path.join(base_dir, "Model")

controller = BugIntelligenceController(
    static_index=os.path.join(model_dir, "static_faiss.index"),
    static_meta=os.path.join(model_dir, "static_metadata.csv"),
    dynamic_index=os.path.join(model_dir, "dynamic_faiss.index"),
    dynamic_meta=os.path.join(model_dir, "dynamic_metadata.csv"),
    api_key=os.getenv("GROQ_API_KEY")
)

print("✅ System Ready!")

# Request/Response Models
class BugQuery(BaseModel):
    query: str

class BugAnalysisResponse(BaseModel):
    query: str
    severity: str
    severity_color: str
    fix_suggestion: str
    num_contexts: int

# API Endpoints
@app.post("/api/analyze", response_model=BugAnalysisResponse)
async def analyze_bug(bug: BugQuery):
    """Analyze bug using multi-agent system"""
    try:
        result = controller.analyze_bug(bug.query)
        return BugAnalysisResponse(
            query=result["query"],
            severity=result["severity"],
            severity_color=result["severity_color"],
            fix_suggestion=result["fix_suggestion"],
            num_contexts=result["num_contexts"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/severity")
async def check_severity(bug: BugQuery):
    """Quick severity check"""
    try:
        contexts = controller.retriever.search(bug.query, k_static=2, k_dynamic=2)
        severity = controller.severity_model.predict(bug.query, use_context=True, contexts=contexts)
        return {
            "query": bug.query,
            "severity": severity,
            "severity_color": controller.severity_model.get_severity_color(severity)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "total_bugs": 277949,
        "static_knowledge": 260000,
        "dynamic_knowledge": 17949,
        "languages": 8,
        "agents_active": 5
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agents": "active"}

# Serve frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
