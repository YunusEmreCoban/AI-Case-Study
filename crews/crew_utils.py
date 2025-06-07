import json
from crewai import TaskOutput
from langchain_openai import AzureChatOpenAI
from crewai import LLM

def azure_llm_provider():
    azure_llm = LLM(
        model="azure/emre-gpt-4o",
        api_base="https://carbondeck-prod-aoi.openai.azure.com/openai/deployments/emre-gpt-4o/chat/completions?api-version=2025-01-01-preview",  # base URL only, no /openai...
        api_key="BabjF1jprtczL0vlzEyo0bkzb9Z1VStRTJXh11sU9JIRmEHe0jhLJQQJ99BDACfhMk5XJ3w3AAABACOG0qrD"
    )
    return azure_llm

def has_candidates(output: TaskOutput) -> bool:
    try:
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