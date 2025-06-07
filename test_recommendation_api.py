import requests
from tqdm import tqdm

BASE_URL = "http://127.0.0.1:8000"
N_RUNS = 1

EXPECTED_ERROR = {
    "error": {
        "code": "ERR_NO_ACTIVITY",
        "message": "No activity found for analysis."
    }
}

single_partial_history = {
    "scope": "1.1",
    "scopeName": "Stationary Combustion",
    "recommendationAmount": 2,
    "activityId": "uuid-2",
    "activityName": "Diesel",
    "organizationId": "dummy-org-id",
    "recommendationHistory": [
        "Replace diesel generators with solar PV"
    ]
}

single_full_history = {
    "scope": "1.1",
    "scopeName": "Stationary Combustion",
    "recommendationAmount": 2,
    "activityId": "uuid-2",
    "activityName": "Diesel",
    "organizationId": "dummy-org-id",
    "recommendationHistory": [
        "Replace diesel generators with solar PV",
        "Conduct staff training on eco-driving"
    ]
}

multi_valid = {
    "scope": "1.1",
    "scopeName": "Stationary Combustion",
    "maxRecommendationAmount": 2,
    "activities": [
        {"id": "uuid-1", "name": "Natural Gas"},
        {"id": "uuid-2", "name": "Diesel"}
    ],
    "organizationId": "dummy-org-id"
}

multi_invalid = {
    "scope": "1.1",
    "scopeName": "Stationary Combustion",
    "maxRecommendationAmount": 2,
    "activities": [
        {"id": "uuid-929", "name": "Silver"},
        {"id": "uuid-888", "name": "Coal"}
    ],
    "organizationId": "dummy-org-id"
}

single_invalid = {
    "scope": "1.1",
    "scopeName": "Stationary Combustion",
    "recommendationAmount": 2,
    "activityId": "uuid-229",
    "activityName": "Silver",
    "organizationId": "dummy-org-id",
    "recommendationHistory": []
}

TEST_CASES = [
    {
        "name": "Single (partial history) - should succeed",
        "endpoint": "/recommendations/single-activity",
        "payload": single_partial_history,
        "expect_error": False,
        "expect_len": 1
    },
    {
        "name": "Single (full history) - should error",
        "endpoint": "/recommendations/single-activity",
        "payload": single_full_history,
        "expect_error": True
    },
    {
        "name": "Multi (valid activities) - should succeed",
        "endpoint": "/recommendations/multi-activity",
        "payload": multi_valid,
        "expect_error": False,
        "expect_len": 2
    },
    {
        "name": "Multi (invalid activities) - should error",
        "endpoint": "/recommendations/multi-activity",
        "payload": multi_invalid,
        "expect_error": True
    },
    {
        "name": "Single (invalid activity) - should error",
        "endpoint": "/recommendations/single-activity",
        "payload": single_invalid,
        "expect_error": True
    }
]

def dicts_equal(a, b):
    return a == b

def run_tests():
    results = []
    for test in TEST_CASES:
        fails = 0
        for _ in tqdm(range(N_RUNS), desc=test['name']):
            try:
                response = requests.post(BASE_URL + test['endpoint'], json=test['payload'])
                try:
                    data = response.json()
                except Exception:
                    fails += 1
                    continue
            except Exception:
                fails += 1
                continue

            if test["expect_error"]:
                if response.status_code != 400 or not dicts_equal(data, EXPECTED_ERROR):
                    fails += 1
            else:
                if response.status_code != 200 or "recommendations" not in data:
                    fails += 1
                else:
                    if "expect_len" in test and len(data["recommendations"]) != test["expect_len"]:
                        fails += 1
                    if test['endpoint'] == "/recommendations/single-activity":
                        for rec in data["recommendations"]:
                            if rec["recommendation"] in test["payload"].get("recommendationHistory", []):
                                fails += 1
        results.append((test['name'], fails))

    print("\n=== SUMMARY ===")
    for name, fails in results:
        print(f"{name}: {'PASS' if fails == 0 else f'{fails} FAILS'}")

if __name__ == "__main__":
    run_tests()