from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import joblib
import os
import logging
from contextlib import asynccontextmanager

# Import AI models and services
from models.case_prioritizer import CasePrioritizer
from models.recovery_predictor import RecoveryPredictor
from models.dca_scorer import DCAScorer
from services.data_processor import DataProcessor
from services.analytics_engine import AnalyticsEngine
from services.prediction_service import PredictionService
from config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for models
models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application lifecycle"""
    # Startup
    logger.info("Starting AI Services...")
    
    # Initialize models
    try:
        models['case_prioritizer'] = CasePrioritizer()
        models['recovery_predictor'] = RecoveryPredictor()
        models['dca_scorer'] = DCAScorer()
        models['data_processor'] = DataProcessor()
        models['analytics_engine'] = AnalyticsEngine()
        models['prediction_service'] = PredictionService()
        
        logger.info("All AI models initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize models: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Services...")

# Create FastAPI app
app = FastAPI(
    title="DCA Management AI Services",
    description="AI/ML services for Debt Collection Agency Management Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security
security = HTTPBearer()
settings = get_settings()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class CaseData(BaseModel):
    caseId: str
    customerId: str
    debtAmount: float = Field(..., gt=0, description="Debt amount must be positive")
    agingDays: int = Field(..., ge=0, description="Aging days must be non-negative")
    customerRiskProfile: str = Field(..., regex="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    invoiceDate: str
    dueDate: str
    serviceType: Optional[str] = "STANDARD"
    previousInteractions: Optional[int] = 0
    paymentHistory: Optional[List[Dict]] = []
    customerSegment: Optional[str] = "STANDARD"
    
    class Config:
        schema_extra = {
            "example": {
                "caseId": "CASE-2024-000001",
                "customerId": "CUST-12345",
                "debtAmount": 5000.00,
                "agingDays": 45,
                "customerRiskProfile": "MEDIUM",
                "invoiceDate": "2024-01-15",
                "dueDate": "2024-02-15",
                "serviceType": "STANDARD",
                "previousInteractions": 2,
                "paymentHistory": [],
                "customerSegment": "STANDARD"
            }
        }

class DCAPerformanceData(BaseModel):
    dcaId: str
    name: str
    totalCasesHandled: int = Field(..., ge=0)
    totalRecovered: float = Field(..., ge=0)
    averageRecoveryRate: float = Field(..., ge=0, le=100)
    averageResolutionTime: float = Field(..., gt=0)
    slaCompliance: float = Field(..., ge=0, le=100)
    customerSatisfactionScore: float = Field(..., ge=0, le=5)
    specializations: List[str] = []
    capacity: Dict[str, Any] = {}
    
    class Config:
        schema_extra = {
            "example": {
                "dcaId": "DCA-001",
                "name": "Premium Collections Inc",
                "totalCasesHandled": 1500,
                "totalRecovered": 750000.00,
                "averageRecoveryRate": 68.5,
                "averageResolutionTime": 45.2,
                "slaCompliance": 92.3,
                "customerSatisfactionScore": 4.2,
                "specializations": ["COMMERCIAL_DEBT", "ENTERPRISE"],
                "capacity": {
                    "maxCases": 500,
                    "currentCases": 320,
                    "availableAgents": 25
                }
            }
        }

class BatchCaseData(BaseModel):
    cases: List[CaseData]
    
class PredictionResponse(BaseModel):
    caseId: str
    recoveryProbability: float = Field(..., ge=0, le=1)
    priorityScore: float = Field(..., ge=0, le=100)
    riskScore: float = Field(..., ge=0, le=100)
    recommendedActions: List[str]
    confidence: float = Field(..., ge=0, le=1)
    predictionTimestamp: datetime = Field(default_factory=datetime.now)

class DCAScoreResponse(BaseModel):
    dcaId: str
    name: str
    performanceScore: float = Field(..., ge=0, le=100)
    reliabilityScore: float = Field(..., ge=0, le=100)
    efficiencyScore: float = Field(..., ge=0, le=100)
    overallRating: float = Field(..., ge=0, le=100)
    ranking: int = Field(..., gt=0)
    strengths: List[str]
    improvements: List[str]
    scoreTimestamp: datetime = Field(default_factory=datetime.now)

class OptimizationRequest(BaseModel):
    cases: List[CaseData]
    availableDCAs: List[DCAPerformanceData]
    constraints: Optional[Dict[str, Any]] = {}

class AssignmentResponse(BaseModel):
    caseId: str
    recommendedDCA: Optional[str]
    matchScore: float = Field(..., ge=0, le=100)
    priority: float = Field(..., ge=0, le=100)
    reasoning: str
    alternativeDCAs: Optional[List[Dict[str, Any]]] = []

# Dependency to get models
def get_models():
    return models

# Authentication dependency (simplified for demo)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # In production, validate JWT token here
    return {"user_id": "demo_user", "role": "admin"}

# Health check endpoints
@app.get("/")
async def root():
    return {
        "service": "DCA Management AI Services",
        "version": "1.0.0",
        "status": "healthy",
        "models": {
            "recovery_predictor": "loaded" if models.get('recovery_predictor') else "not_loaded",
            "case_prioritizer": "loaded" if models.get('case_prioritizer') else "not_loaded",
            "dca_scorer": "loaded" if models.get('dca_scorer') else "not_loaded"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": len(models) > 0,
        "uptime": "N/A"  # Could track actual uptime
    }

# AI/ML Endpoints

@app.post("/predict/recovery", response_model=PredictionResponse)
async def predict_recovery(
    case_data: CaseData,
    background_tasks: BackgroundTasks,
    models_dict: dict = Depends(get_models),
    current_user: dict = Depends(get_current_user)
):
    """Predict recovery probability for a single case"""
    try:
        logger.info(f"Processing recovery prediction for case: {case_data.caseId}")
        
        # Process case data
        features = models_dict['data_processor'].process_case_features(case_data.dict())
        
        # Get predictions
        recovery_prob = models_dict['recovery_predictor'].predict_probability(features)
        priority_score = models_dict['case_prioritizer'].calculate_priority(features)
        risk_score = models_dict['case_prioritizer'].calculate_risk_score(features)
        
        # Generate recommendations
        recommendations = _generate_recommendations(case_data, recovery_prob, priority_score, risk_score)
        
        # Calculate confidence based on data quality and model certainty
        confidence = _calculate_prediction_confidence(case_data, recovery_prob)
        
        # Log prediction for model improvement (background task)
        background_tasks.add_task(
            _log_prediction,
            case_data.caseId,
            recovery_prob,
            priority_score,
            risk_score
        )
        
        return PredictionResponse(
            caseId=case_data.caseId,
            recoveryProbability=float(recovery_prob),
            priorityScore=float(priority_score),
            riskScore=float(risk_score),
            recommendedActions=recommendations,
            confidence=float(confidence)
        )
        
    except Exception as e:
        logger.error(f"Prediction error for case {case_data.caseId}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict/batch", response_model=List[PredictionResponse])
async def predict_batch_recovery(
    batch_data: BatchCaseData,
    background_tasks: BackgroundTasks,
    models_dict: dict = Depends(get_models),
    current_user: dict = Depends(get_current_user)
):
    """Predict recovery probability for multiple cases"""
    try:
        logger.info(f"Processing batch prediction for {len(batch_data.cases)} cases")
        
        predictions = []
        
        for case_data in batch_data.cases:
            try:
                features = models_dict['data_processor'].process_case_features(case_data.dict())
                
                recovery_prob = models_dict['recovery_predictor'].predict_probability(features)
                priority_score = models_dict['case_prioritizer'].calculate_priority(features)
                risk_score = models_dict['case_prioritizer'].calculate_risk_score(features)
                
                recommendations = _generate_recommendations(case_data, recovery_prob, priority_score, risk_score)
                confidence = _calculate_prediction_confidence(case_data, recovery_prob)
                
                predictions.append(PredictionResponse(
                    caseId=case_data.caseId,
                    recoveryProbability=float(recovery_prob),
                    priorityScore=float(priority_score),
                    riskScore=float(risk_score),
                    recommendedActions=recommendations,
                    confidence=float(confidence)
                ))
                
            except Exception as case_error:
                logger.error(f"Error processing case {case_data.caseId}: {str(case_error)}")
                # Continue with other cases, add default prediction
                predictions.append(PredictionResponse(
                    caseId=case_data.caseId,
                    recoveryProbability=0.5,
                    priorityScore=50.0,
                    riskScore=50.0,
                    recommendedActions=["Manual review required"],
                    confidence=0.1
                ))
        
        # Log batch prediction
        background_tasks.add_task(
            _log_batch_prediction,
            len(batch_data.cases),
            len([p for p in predictions if p.confidence > 0.5])
        )
        
        return predictions
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")

@app.post("/score/dca", response_model=DCAScoreResponse)
async def score_dca_performance(
    dca_data: DCAPerformanceData,
    models_dict: dict = Depends(get_models),
    current_user: dict = Depends(get_current_user)
):
    """Score DCA performance and generate ranking"""
    try:
        logger.info(f"Scoring DCA performance for: {dca_data.dcaId}")
        
        # Calculate performance scores
        performance_score = models_dict['dca_scorer'].calculate_performance_score(dca_data.dict())
        reliability_score = models_dict['dca_scorer'].calculate_reliability_score(dca_data.dict())
        efficiency_score = models_dict['dca_scorer'].calculate_efficiency_score(dca_data.dict())
        
        # Calculate overall rating
        overall_rating = (performance_score + reliability_score + efficiency_score) / 3
        
        # Generate insights
        strengths, improvements = models_dict['dca_scorer'].generate_insights(dca_data.dict())
        
        # Calculate ranking (simplified - in production, compare against all DCAs)
        ranking = _calculate_dca_ranking(overall_rating)
        
        return DCAScoreResponse(
            dcaId=dca_data.dcaId,
            name=dca_data.name,
            performanceScore=float(performance_score),
            reliabilityScore=float(reliability_score),
            efficiencyScore=float(efficiency_score),
            overallRating=float(overall_rating),
            ranking=ranking,
            strengths=strengths,
            improvements=improvements
        )
        
    except Exception as e:
        logger.error(f"DCA scoring error for {dca_data.dcaId}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"DCA scoring error: {str(e)}")

@app.post("/optimize/assignment")
async def optimize_case_assignment(
    request: OptimizationRequest,
    models_dict: dict = Depends(get_models),
    current_user: dict = Depends(get_current_user)
):
    """Optimize case assignment to DCAs using AI"""
    try:
        logger.info(f"Optimizing assignment for {len(request.cases)} cases to {len(request.availableDCAs)} DCAs")
        
        assignments = []
        
        # Sort cases by priority
        case_priorities = []
        for case in request.cases:
            features = models_dict['data_processor'].process_case_features(case.dict())
            priority = models_dict['case_prioritizer'].calculate_priority(features)
            case_priorities.append((case, priority))
        
        case_priorities.sort(key=lambda x: x[1], reverse=True)
        
        # Assign cases to best matching DCAs
        for case_data, priority in case_priorities:
            best_match = _find_best_dca_match(
                case_data, 
                request.availableDCAs, 
                models_dict['dca_scorer'],
                request.constraints
            )
            
            assignments.append(AssignmentResponse(
                caseId=case_data.caseId,
                recommendedDCA=best_match["dcaId"] if best_match else None,
                matchScore=best_match["score"] if best_match else 0,
                priority=priority,
                reasoning=best_match["reasoning"] if best_match else "No suitable DCA found",
                alternativeDCAs=best_match.get("alternatives", [])
            ))
        
        return {"assignments": assignments}
        
    except Exception as e:
        logger.error(f"Assignment optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Assignment optimization error: {str(e)}")

@app.get("/analytics/trends")
async def get_recovery_trends(
    models_dict: dict = Depends(get_models),
    current_user: dict = Depends(get_current_user)
):
    """Get recovery trends and patterns"""
    try:
        # Use analytics engine to generate trends
        trends = models_dict['analytics_engine'].generate_recovery_trends()
        
        return trends
        
    except Exception as e:
        logger.error(f"Trends analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Trends analysis error: {str(e)}")

@app.get("/analytics/performance")
async def get_performance_analytics(
    period: str = "30d",
    models_dict: dict = Depends(get_models),
    current_user: dict = Depends(get_current_user)
):
    """Get performance analytics"""
    try:
        analytics = models_dict['analytics_engine'].generate_performance_analytics(period)
        
        return analytics
        
    except Exception as e:
        logger.error(f"Performance analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Performance analytics error: {str(e)}")

# Model management endpoints
@app.post("/models/retrain")
async def retrain_models(
    background_tasks: BackgroundTasks,
    models_dict: dict = Depends(get_models),
    current_user: dict = Depends(get_current_user)
):
    """Trigger model retraining"""
    try:
        # Add retraining task to background
        background_tasks.add_task(_retrain_models, models_dict)
        
        return {
            "message": "Model retraining initiated",
            "status": "in_progress",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Model retraining error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model retraining error: {str(e)}")

@app.get("/models/status")
async def get_model_status(
    models_dict: dict = Depends(get_models),
    current_user: dict = Depends(get_current_user)
):
    """Get status of all AI models"""
    try:
        status = {}
        
        for model_name, model in models_dict.items():
            if hasattr(model, 'get_status'):
                status[model_name] = model.get_status()
            else:
                status[model_name] = {
                    "loaded": True,
                    "last_updated": "N/A",
                    "version": "1.0.0"
                }
        
        return {
            "models": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Model status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model status error: {str(e)}")

# Helper functions
def _generate_recommendations(case_data: CaseData, recovery_prob: float, priority_score: float, risk_score: float) -> List[str]:
    """Generate actionable recommendations based on AI predictions"""
    recommendations = []
    
    if recovery_prob > 0.8:
        recommendations.append("High recovery probability - prioritize immediate contact")
        recommendations.append("Consider offering early payment discount")
    elif recovery_prob > 0.6:
        recommendations.append("Moderate recovery probability - standard collection process")
        recommendations.append("Schedule follow-up within 48 hours")
    else:
        recommendations.append("Low recovery probability - consider alternative strategies")
        recommendations.append("Evaluate for legal action or write-off")
    
    if case_data.agingDays > 90:
        recommendations.append("Case is significantly aged - escalate urgently")
        recommendations.append("Consider skip tracing if contact information is outdated")
    elif case_data.agingDays > 60:
        recommendations.append("Case aging - increase contact frequency")
    
    if case_data.debtAmount > 10000:
        recommendations.append("High-value case - assign to senior agent")
        recommendations.append("Consider payment plan options")
    
    if case_data.customerRiskProfile == "HIGH":
        recommendations.append("High-risk customer - use specialized approach")
        recommendations.append("Document all interactions thoroughly")
    
    if priority_score > 80:
        recommendations.append("High priority case - immediate action required")
    
    if risk_score > 70:
        recommendations.append("High-risk case - proceed with caution")
        recommendations.append("Ensure compliance with all regulations")
    
    return recommendations

def _calculate_prediction_confidence(case_data: CaseData, recovery_prob: float) -> float:
    """Calculate confidence score for predictions"""
    confidence = 0.7  # Base confidence
    
    # Adjust based on data completeness
    if case_data.paymentHistory:
        confidence += 0.1
    if case_data.previousInteractions > 0:
        confidence += 0.1
    if case_data.agingDays > 0:
        confidence += 0.05
    
    # Adjust based on prediction certainty
    if recovery_prob > 0.8 or recovery_prob < 0.2:
        confidence += 0.1  # More confident in extreme predictions
    
    return min(1.0, confidence)

def _calculate_dca_ranking(overall_rating: float) -> int:
    """Calculate DCA ranking based on overall rating"""
    # Simplified ranking - in production, compare against all DCAs
    if overall_rating >= 90:
        return 1
    elif overall_rating >= 80:
        return 2
    elif overall_rating >= 70:
        return 3
    elif overall_rating >= 60:
        return 4
    else:
        return 5

def _find_best_dca_match(case_data: CaseData, available_dcas: List[DCAPerformanceData], dca_scorer, constraints: Dict) -> Optional[Dict]:
    """Find the best DCA match for a case"""
    best_match = None
    best_score = 0
    alternatives = []
    
    for dca in available_dcas:
        # Calculate match score based on various factors
        score = 0
        reasoning = []
        
        # Capacity check
        current_cases = dca.capacity.get("currentCases", 0)
        max_cases = dca.capacity.get("maxCases", 1000)
        
        if current_cases >= max_cases:
            continue  # Skip if at capacity
        
        # Specialization match
        if case_data.serviceType in dca.specializations:
            score += 30
            reasoning.append("Specialization match")
        
        # Performance score
        score += dca.averageRecoveryRate * 0.4
        
        # SLA compliance
        score += dca.slaCompliance * 0.3
        
        # Capacity utilization (prefer less utilized DCAs)
        utilization = current_cases / max_cases if max_cases > 0 else 1
        score += (1 - utilization) * 20
        
        # Customer satisfaction
        score += (dca.customerSatisfactionScore / 5) * 10
        
        # Apply constraints
        if constraints:
            # Example: preferred DCAs
            if constraints.get("preferredDCAs") and dca.dcaId in constraints["preferredDCAs"]:
                score += 15
                reasoning.append("Preferred DCA")
        
        match_info = {
            "dcaId": dca.dcaId,
            "name": dca.name,
            "score": score,
            "reasoning": "; ".join(reasoning) if reasoning else "General performance match"
        }
        
        if score > best_score:
            if best_match:
                alternatives.append(best_match)
            best_score = score
            best_match = match_info
        elif len(alternatives) < 3:  # Keep top 3 alternatives
            alternatives.append(match_info)
    
    if best_match:
        best_match["alternatives"] = alternatives
    
    return best_match

# Background task functions
async def _log_prediction(case_id: str, recovery_prob: float, priority_score: float, risk_score: float):
    """Log prediction for model improvement"""
    logger.info(f"Logged prediction for case {case_id}: recovery={recovery_prob:.3f}, priority={priority_score:.1f}")

async def _log_batch_prediction(total_cases: int, successful_predictions: int):
    """Log batch prediction statistics"""
    logger.info(f"Batch prediction completed: {successful_predictions}/{total_cases} successful")

async def _retrain_models(models_dict: dict):
    """Retrain AI models with latest data"""
    logger.info("Starting model retraining process...")
    # In production, this would fetch latest data and retrain models
    logger.info("Model retraining completed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )