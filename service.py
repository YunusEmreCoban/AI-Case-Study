import json
import pathlib
from typing import Union
from models import (
    ErrorDetail,
    MultiActivityRequest,
    SingleActivityRequest,
    RecommendationResponse,
    ErrorResponse,
)
from crews.crew_multi import MultiRecommendationCrew
from crews.crew_single import SingleRecommendationCrew

DATA = json.loads(pathlib.Path(r"data/dummy_recommendations.json").read_text(encoding="utf-8"))
print("[DEBUG] DATA loaded:", DATA)

multi_crew_builder = MultiRecommendationCrew()
single_crew_builder = SingleRecommendationCrew()

def no_activity_error(message="No activity found for analysis."):
    return ErrorResponse(
        error=ErrorDetail(
            code="ERR_NO_ACTIVITY",
            message=message,
        )
    )

def _parse_output(out) -> Union[list, ErrorResponse]:
    try:
        result = out.json_dict if hasattr(out, "json_dict") and out.json_dict else json.loads(out.raw)
        # Handle JSON boolean false and string "false"
        if result is False or (isinstance(result, str) and result.strip().lower() == "false"):
            return no_activity_error()

        # Handle {"recommendations": ...}
        if isinstance(result, dict) and "recommendations" in result:
            recs = result["recommendations"]
            if not recs:
                return no_activity_error()
            return recs

    except Exception:
        return no_activity_error("Crew returned non-dict or corrupt output")

def _run_crew_multi(ids, names, k):
    out = multi_crew_builder.multi_crew().kickoff(
        inputs={
            "activity_ids": ids,
            "activity_names": names,
            "maxRecommendationAmount": k,
            "all_records": DATA,
        }
    )
    return _parse_output(out)

def _run_crew_single(ids, names, k, history):
    out = single_crew_builder.single_crew().kickoff(
        inputs={
            "activity_ids": ids,
            "activity_names": names,
            "maxRecommendationAmount": k,
            "history": history,
            "all_records": DATA,
        }
    )
    return _parse_output(out)

def multi_activity_service(req: MultiActivityRequest):
    ids = [a.id for a in req.activities]
    names = [a.name for a in req.activities]
    recs = _run_crew_multi(ids, names, req.maxRecommendationAmount)
    if isinstance(recs, ErrorResponse):
        return recs
    if not recs:
        return no_activity_error()
    return RecommendationResponse(recommendations=recs)

def single_activity_service(req: SingleActivityRequest):
    recs = _run_crew_single(
        [req.activityId], [req.activityName],
        req.recommendationAmount,
        req.recommendationHistory
    )
    if isinstance(recs, ErrorResponse):
        return recs
    if not recs:
        return no_activity_error()
    return RecommendationResponse(recommendations=recs)