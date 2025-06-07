from fastapi import FastAPI
from models import (
    MultiActivityRequest, SingleActivityRequest,
    ErrorResponse
)
from service import multi_activity_service, single_activity_service
from fastapi.responses import ORJSONResponse

app = FastAPI(
    title="AI Agent Case Study API",
    version="1.0.0",
    description="CrewAI multi-agent solution",
    default_response_class=ORJSONResponse
)

@app.post(
    "/recommendations/multi-activity",
    response_class=ORJSONResponse, 
    responses={400: {"model": ErrorResponse}}
)
def recommend_multi(req: MultiActivityRequest):
    result = multi_activity_service(req)
    if isinstance(result, ErrorResponse):
        return  ORJSONResponse(status_code=400, content=result.model_dump())
    return result

@app.post(
    "/recommendations/single-activity",
    response_class=ORJSONResponse, 
    responses={400: {"model": ErrorResponse}}
)
def recommend_single(req: SingleActivityRequest):
    result = single_activity_service(req)
    if isinstance(result, ErrorResponse):
        return ORJSONResponse(status_code=400, content=result.model_dump())
    return result
