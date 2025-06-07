from typing import List, Literal, Optional
from pydantic import BaseModel, Field

ImpactLevel = Literal["HIGH", "MEDIUM", "LOW"]
FeasibilityLevel = Literal["HIGH", "MEDIUM", "LOW"]

class Activity(BaseModel):
    id: str
    name: str

class MultiActivityRequest(BaseModel):
    scope: str
    scopeName: str
    maxRecommendationAmount: int = Field(..., gt=0)
    activities: List[Activity]
    organizationId: str

class SingleActivityRequest(BaseModel):
    scope: str
    scopeName: str
    recommendationAmount: int = Field(..., gt=0)
    activityId: str
    activityName: str
    organizationId: str
    recommendationHistory: List[str] = []

class Recommendation(BaseModel):
    activityId: str
    activityName: str
    scope: str
    recommendation: str
    impactLevel: ImpactLevel
    estimatedReductionPercentage: float
    feasibilityScore: float
    feasibilityLevel: FeasibilityLevel
    cost: float
    infrastructureRequirements: str
    technologyStatus: str

    
class RecommendationResponse(BaseModel):
    recommendations: List[Recommendation]
    tokenUsage: Optional[int] = None

class ErrorDetail(BaseModel):
    code: str
    message: str

class ErrorResponse(BaseModel):
    error: ErrorDetail