import json
from crewai import TaskOutput

def has_candidates(output: TaskOutput) -> bool:
    try:
        # Extracts list of candidates from output
        data = None
        # CrewAI v0.27+ uses output.json_dict for LLM outputs, output.raw otherwise
        if hasattr(output, "json_dict") and output.json_dict is not None:
            data = output.json_dict
        elif hasattr(output, "raw") and output.raw is not None:
            # raw is string (JSON)
            try:
                data = json.loads(output.raw)
            except Exception:
                data = output.raw
        else:
            data = output  # fallback

        # Handle boolean 'false' or string "false"
        if data is False or (isinstance(data, str) and data.strip().lower() == "false"):
            return False

        if isinstance(data, list):
            return len(data) > 0

        if isinstance(data, dict):
            if "recommendations" in data and isinstance(data["recommendations"], list):
                return len(data["recommendations"]) > 0
            return False

        return False
    except Exception:
        return False