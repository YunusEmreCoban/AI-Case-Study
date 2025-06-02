from datetime import datetime
import json
import os
import sys
import requests

BASE_URL = "http://127.0.0.1:8000"


payload = {
    "scope": "1.1",
    "scopeName": "Stationary Combustion",
    "maxRecommendationAmount": 2,
    "activities": [
        {"id": "uuid-1", "name": "Natural Gas"},
        {"id": "uuid-2", "name": "Diesel"},
        {"id": "uuid-3", "name": "Diesel"}
    ],
    "organizationId": "dummy-org-id"
}

def main():
    try:
        r = requests.post(
            f"{BASE_URL}/recommendations/multi-activity",
            json=payload,
            timeout=30
        )
        r.raise_for_status()
    except requests.RequestException as e:
        sys.exit(f"Request failed: {e}")

    print(f"{r.status_code}")
    print(json.dumps(r.json(), indent=2))


def main():
    os.makedirs("test_logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_path = f"test_logs/test_multi_activity_input_{timestamp}.txt"
    output_path = f"test_logs/test_multi_activity_output_{timestamp}.txt"

    with open(input_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(payload, indent=2))

    print("Request Input:")
    print(json.dumps(payload, indent=2))

    try:
        r = requests.post(
            f"{BASE_URL}/recommendations/multi-activity",
            json=payload,
            timeout=30
        )
        r.raise_for_status()
    except requests.RequestException as e:
        sys.exit(f"Request failed: {e}")

    print(f"HTTP Status: {r.status_code}")
    print("Response Output:")
    print(json.dumps(r.json(), indent=2))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(r.json(), indent=2))

if __name__ == "__main__":
    main()