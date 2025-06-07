import json
import pathlib
from typing import Union, Tuple
from models import (
    ErrorDetail,
    MultiActivityRequest,
    SingleActivityRequest,
    RecommendationResponse,
    ErrorResponse,
)
from crews.crew_multi import MultiRecommendationCrew
from crews.crew_single import SingleRecommendationCrew

DATA = json.loads(pathlib.Path("data/dummy_recommendations.json").read_text(encoding="utf-8"))
print("[DEBUG] DATA loaded:", DATA)


def no_activity_error(message: str = "No activity found for analysis.") -> ErrorResponse:
    return ErrorResponse(error=ErrorDetail(code="ERR_NO_ACTIVITY", message=message))

def parse_output(out) -> Union[Tuple[list, int], ErrorResponse]:
    """Extracts recommendations and token usage, or returns an error."""
    try:
        result = out.json_dict if hasattr(out, "json_dict") and out.json_dict else json.loads(out.raw)
        token_count = out.token_usage.total_tokens

        # Handle explicit false-y responses for if matcher return falses
        if result is False or (isinstance(result, str) and result.strip().lower() == "false"):
            return no_activity_error()
        if isinstance(result, dict) and "recommendations" in result:
            recs = result["recommendations"]
            if not recs:
                return no_activity_error()
            return recs, token_count
    except Exception:
        return no_activity_error("Crew returned non-dict or corrupt output")

def run_crew(crew, ids, names, k, history=None) -> Union[Tuple[list, int], ErrorResponse]:
    """Generic crew runner for single or multi."""
    inputs = {
        "activity_ids": ids,
        "activity_names": names,
        "maxRecommendationAmount": k,
        "all_records": DATA,
    }
    if history is not None:
        inputs["history"] = history
    out = crew.kickoff(inputs=inputs)
    return parse_output(out)

def multi_activity_service(req: MultiActivityRequest) -> Union[RecommendationResponse, ErrorResponse]:
    ids = [a.id for a in req.activities]
    names = [a.name for a in req.activities]
    multi_crew = MultiRecommendationCrew()
    result = run_crew(multi_crew.multi_crew(), ids, names, req.maxRecommendationAmount)
    if isinstance(result, ErrorResponse):
        return result
    recs, token_usage = result
    return RecommendationResponse(recommendations=recs, tokenUsage=token_usage)

def single_activity_service(req: SingleActivityRequest) -> Union[RecommendationResponse, ErrorResponse]:
    single_crew = SingleRecommendationCrew()
    result = run_crew(
        single_crew.single_crew(),
        [req.activityId], [req.activityName],
        req.recommendationAmount,
        req.recommendationHistory
    )
    if isinstance(result, ErrorResponse):
        return result
    recs, token_usage = result
    return RecommendationResponse(recommendations=recs, tokenUsage=token_usage)