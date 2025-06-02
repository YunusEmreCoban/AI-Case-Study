import json
import os
import sys
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

payload = {
    "scope": "1.1",
    "scopeName": "Stationary Combustion",
    "recommendationAmount": 2,
    "activityId": "uuid-2",
    "activityName": "Diesel",
    "organizationId": "dummy-org-id",
    "recommendationHistory": [
        "Conduct staff training on eco-driving",
    ]
}

def main():
    os.makedirs("test_logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_path = f"test_logs/input_single_activity_{timestamp}.txt"
    output_path = f"test_logs/output_single_activity_{timestamp}.txt"

    with open(input_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(payload, indent=2))

    print("Request Input:")
    print(json.dumps(payload, indent=2))

    try:
        r = requests.post(
            f"{BASE_URL}/recommendations/single-activity",
            json=payload,
            timeout=30
        )
        data = r.json()
    except requests.RequestException as e:
        sys.exit(f"Network error: {e}")
    except ValueError:
        sys.exit("Invalid JSON in response")

    print(f"HTTP {r.status_code}")
    print("Response Output:")
    print(json.dumps(data, indent=2))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2))

    if r.status_code == 200:
        print("Success response")
        assert "recommendations" in data, "Missing recommendations key"
        assert len(data["recommendations"]) <= payload["recommendationAmount"], "Too many items returned"
        for rec in data["recommendations"]:
            assert rec["recommendation"] not in payload["recommendationHistory"], "History item leaked into result"

    elif r.status_code == 400:
        print("Error response (as expected)")
        assert "error" in data, "Missing error key"
        assert data["error"]["code"] == "ERR_NO_ACTIVITY"
        assert data["error"]["message"] == "No activity found for analysis."

    else:
        sys.exit(f"Unexpected status code: {r.status_code}")

if __name__ == "__main__":
    main()