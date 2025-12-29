"""
FlightSense Application Entry Point

This is the main application file that initializes the FastAPI server
and orchestrates all FlightSense services.
"""
from __future__ import annotations
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime, date

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from models.enums.enums import UserRole, Departments

# Import database services
from services.db_service.mysql_db_service import MySQLDbService

# Import orchestrator
from services.orchestrator.orchestrator import FlightSenseOrchestrator
from services.orchestrator.filter import DataFilter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------

# Database selection
USE_MYSQL = os.getenv("USE_MYSQL", "false").lower() == "true"
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")

# Global orchestrator instance
orchestrator: Optional[FlightSenseOrchestrator] = None


# -------------------------------------------------------------------------
# LIFESPAN MANAGEMENT
# -------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown."""
    global orchestrator
    
    # Startup
    logger.info("Starting FlightSense application...")
    
    try:
        logger.info("Using MySQL database")
        db_service = MySQLDbService()
        
        # Initialize orchestrator with all services
        orchestrator = FlightSenseOrchestrator(db_service, JWT_SECRET)
        
        logger.info("FlightSense initialized successfully")
        logger.info(f"   - Database: {'MySQL' if USE_MYSQL else 'SQLite'}")
        logger.info(f"   - Jira: {'Real' if os.getenv('USE_REAL_JIRA') == 'true' else 'Mock'}")
        logger.info(f"   - LLM Provider: {os.getenv('LLM_PROVIDER', 'openai')}")
        
    except Exception as e:
        logger.error(f"Failed to initialize FlightSense: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down FlightSense...")
        
    if USE_MYSQL and hasattr(db_service, 'close'):
        db_service.close()


# -------------------------------------------------------------------------
# FASTAPI APPLICATION
# -------------------------------------------------------------------------

app = FastAPI(
    title="FlightSense API",
    description="AI-Powered Airline Customer Feedback Analysis & Ticketing System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------------
# DEPENDENCY INJECTION
# -------------------------------------------------------------------------

def get_orchestrator() -> FlightSenseOrchestrator:
    """Dependency to get the global orchestrator instance."""
    if orchestrator is None:
        raise HTTPException(status_code=500, detail="System not initialized")
    return orchestrator


def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    """Extract JWT token from Authorization header."""
    logger.info(f"Authorization header received: {authorization}")
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    return authorization[7:]  # Remove "Bearer " prefix

def require_admin(
    token: str = Depends(get_token_from_header),
    orch: FlightSenseOrchestrator = Depends(get_orchestrator),
):
    """
    Dependency that ensures the caller is an admin user.
    """
    user_info = orch.verify_token(token)

    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if user_info.get("role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required",
        )

    return user_info

# -------------------------------------------------------------------------
# REQUEST/RESPONSE MODELS
# -------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: UserRole = UserRole.VIEWER
    department: Optional[Departments] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class LabelReviewRequest(BaseModel):
    review: str
    max_segments: Optional[int] = None


class ClassifyBatchRequest(BaseModel):
    feedbacks: List[str]
    dates: Optional[List[str]] = None


class FilterRequest(BaseModel):
    limit: Optional[int] = 100
    label_type: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    only_without_ticket: bool = False
      
      
class DepartmentStatisticsRequest(BaseModel):
    department_name: str
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    period: str

class ManagerStatisticsRequest(BaseModel):
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    period: str

class HighPriorityReviewItem(BaseModel):
    label: str
    review: str
    highlightIndex: Optional[str] = None
    date: date
    flightNumber: Optional[str] = None
    route: Optional[str] = None


class DepartmentHighPriorityResponse(BaseModel):
    department: str
    items: List[HighPriorityReviewItem]


class ManagerHighPriorityResponse(BaseModel):
    departments: Dict[str, List[HighPriorityReviewItem]]
      

# -------------------------------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------------------------------
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "FlightSense API",
        "database": "MySQL" if USE_MYSQL else "SQLite",
        "jira": "Real" if os.getenv("USE_REAL_JIRA") == "true" else "Mock",
    }


@app.get("/api/version")
async def get_version():
    """Get API version information."""
    return {
        "version": "1.0.0",
        "service": "FlightSense API",
    }


# -------------------------------------------------------------------------
# AUTHENTICATION ENDPOINTS
# -------------------------------------------------------------------------

@app.post("/api/auth/register")
async def register(
    request: RegisterRequest,
    _: Dict = Depends(require_admin),
    orch: FlightSenseOrchestrator = Depends(get_orchestrator)
):
    """Register a new user."""
    result = orch.register_user(
        username=request.username,
        email=request.email,
        password=request.password,
        role=request.role,
        department=request.department,
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@app.post("/api/auth/login")
async def login(
    request: LoginRequest,
    orch: FlightSenseOrchestrator = Depends(get_orchestrator)
):
    """Login and get JWT token."""
    result = orch.login(request.username, request.password)
    
    if not result.get("success"):
        raise HTTPException(status_code=401, detail=result.get("error"))
    
    return result


# -------------------------------------------------------------------------
# DATA ENDPOINTS
# -------------------------------------------------------------------------

@app.post("/api/data/feedback")
async def get_feedback(
    request: FilterRequest,
    token: str = Depends(get_token_from_header),
    orch: FlightSenseOrchestrator = Depends(get_orchestrator)
):
    """Get filtered feedback data."""
    result = orch.get_processed_data_filtered(token, request.dict())
    
    if not result.get("success"):
        raise HTTPException(status_code=403, detail=result.get("error"))
    
    return result


@app.get("/api/data/dashboard")
async def get_dashboard(
    page: str = "dashboard",
    token: str = Depends(get_token_from_header),
    orch: FlightSenseOrchestrator = Depends(get_orchestrator)
):
    """Get dashboard summary."""
    result = orch.get_dashboard_summary(token, page)
    
    if not result.get("success"):
        raise HTTPException(status_code=403, detail=result.get("error"))
    
    return result


@app.get("/api/data/analytics/{label}")
async def get_analytics(
    label: str,
    token: str = Depends(get_token_from_header),
    orch: FlightSenseOrchestrator = Depends(get_orchestrator)
):
    """Get analytics for a specific label."""
    result = orch.get_category_analytics(token, label)
    
    if not result.get("success"):
        raise HTTPException(status_code=403, detail=result.get("error"))
    
    return result


# -------------------------------------------------------------------------
# REPORTING ENDPOINTS
# -------------------------------------------------------------------------

@app.post("/api/reporting/label")
async def label_review(
    request: LabelReviewRequest,
    orch: FlightSenseOrchestrator = Depends(get_orchestrator)
):
    """Label a single review with fine-grained segments."""
    try:
        result = orch.label_single_review(request.review)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error labeling review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/data/push")
async def push_feedback(
    request: ClassifyBatchRequest,
    token: str = Depends(get_token_from_header),
    orch: FlightSenseOrchestrator = Depends(get_orchestrator)
):
    """Classify and store a batch of feedback."""
    try:
        from packages.llm.classifier import FeedbackClassifier
        from datetime import date
        
        classifier = FeedbackClassifier()
        
        # Parse dates if provided
        dates = None
        if request.dates:
            dates = [date.fromisoformat(d) for d in request.dates]
        
        # Classify
        df = classifier.classify_batch(request.feedbacks, dates)
        
        # Store in database
        result = orch.push_processed_data(token, df)
        
        if not result.get("success"):
            raise HTTPException(status_code=403, detail=result.get("error"))
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reporting/create-tickets")
async def create_tickets(
    request: FilterRequest,
    token: str = Depends(get_token_from_header),
    orch: FlightSenseOrchestrator = Depends(get_orchestrator)
):
    """Create Jira tickets for filtered feedback."""
    result = orch.create_tickets_for_filtered(token, request.dict())
    
    if not result.get("success"):
        raise HTTPException(status_code=403, detail=result.get("error"))
    
    return result


# -------------------------------------------------------------------------
# LISTENER ENDPOINTS
# -------------------------------------------------------------------------

@app.post("/api/listener/run")
async def run_listener(
    token: str = Depends(get_token_from_header),
    orch: FlightSenseOrchestrator = Depends(get_orchestrator)
):
    """Trigger the review listener to process new reviews."""
    # Verify token
    user_info = orch.verify_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Trigger processing
    result = orch.process_new_reviews()
    
    if not result.get("success"):
        # If it failed because listener is not available (e.g. SQLite), return 400 or 503
        if result.get("error") == "ReviewListener not available":
             raise HTTPException(status_code=503, detail="ReviewListener not available (requires MySQL)")
        raise HTTPException(status_code=500, detail=result.get("error"))
    
    return result

  
# -------------------------------------------------------------------------
# STATISTICS ENDPOINTS
# -------------------------------------------------------------------------

@app.post("/api/statistics/department")
async def get_department_statistics(
    request: DepartmentStatisticsRequest,
    token: str = Depends(get_token_from_header),
    orch: FlightSenseOrchestrator = Depends(get_orchestrator)
):
    try:
        result = orch.get_department_stats(token, request.department_name, request.period, request.date_from, request.date_to)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error while accessing department stats: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/statistics/manager")
async def get_manager_statistics(
    request: ManagerStatisticsRequest,
    token: str = Depends(get_token_from_header),
    orch: FlightSenseOrchestrator = Depends(get_orchestrator)
):
    try:
        result = orch.get_manager_stats(token, request.period, request.date_from, request.date_to)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error while accessing manager stats: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# -------------------------------------------------------------------------
# HIGH PRIORITY ENDPOINTS
# -------------------------------------------------------------------------
@app.get("/api/high-priority/department", response_model=DepartmentHighPriorityResponse)
async def get_department_high_priority(
    department: str,
    limit: int = 5,
    token: str = Depends(get_token_from_header),
    orch: FlightSenseOrchestrator = Depends(get_orchestrator),
):
    result = orch.get_department_high_priority_reviews(token, department, limit)

    if not result.get("success"):
        raise HTTPException(status_code=403, detail=result.get("error"))

    items = [
        HighPriorityReviewItem(
            label=r["label"],
            review=r["review"],
            highlightIndex=r.get("highlight_index"),
            date=r["date"],
            flightNumber=r.get("flight_number"),
            route=r.get("route"),
        )
        for r in result["items"]
    ]

    return DepartmentHighPriorityResponse(
        department=result["department"],
        items=items,
    )

@app.get("/api/high-priority/manager", response_model=ManagerHighPriorityResponse)
async def get_manager_high_priority(
    limit_per_department: int = 3,
    token: str = Depends(get_token_from_header),
    orch: FlightSenseOrchestrator = Depends(get_orchestrator),
):
    result = orch.get_manager_high_priority_reviews(token, limit_per_department)

    if not result.get("success"):
        raise HTTPException(status_code=403, detail=result.get("error"))

    departments: Dict[str, List[HighPriorityReviewItem]] = {}

    for dept, rows in result["departments"].items():
        departments[dept] = [
            HighPriorityReviewItem(
                label=r["label"],
                review=r["review"],
                highlightIndex=r.get("highlight_index"),
                date=r["date"],
                flightNumber=r.get("flight_number"),
                route=r.get("route"),
            )
            for r in rows
        ]

    return ManagerHighPriorityResponse(departments=departments)


# -------------------------------------------------------------------------
# MAIN ENTRY POINT
# -------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("ENV", "development") == "development"
    
    logger.info(f"Starting FlightSense API on {host}:{port}")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )

