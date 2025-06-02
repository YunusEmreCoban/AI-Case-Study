import os
import requests
from tqdm import tqdm
from datetime import datetime

# The similiar tests were intended to be run more than once to test for hallucinations.

BASE_URL = "http://127.0.0.1:8000"

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

N_RUNS = 10

def dicts_equal(a, b):
    return a == b

def run_tests():
    os.makedirs("test_logs", exist_ok=True)
    log_file_path = os.path.join("test_logs", "hallucination_test_recommendation_api.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    summary_lines = [f"Test run at {timestamp}\n"]
    detailed_lines = []
    results = []
    for test in TEST_CASES:
        fails = 0
        fail_details = []
        print(f"\nTest: {test['name']}")
        for run_idx in tqdm(range(N_RUNS), desc=test['name']):
            try:
                r = requests.post(BASE_URL + test['endpoint'], json=test['payload'])
                try:
                    data = r.json()
                except Exception as json_exc:
                    # Try to get raw text if not JSON
                    raw_output = getattr(r, "text", "<no text>")
                    msg = (
                        f"[EXCEPTION][{test['name']}] Run {run_idx + 1}: JSON decode error: {json_exc}\n"
                        f"  Raw API response: {raw_output}"
                    )
                    print(f"\n{msg}")
                    fail_details.append(msg)
                    fails += 1
                    continue
            except Exception as e:
                msg = f"[EXCEPTION][{test['name']}] Run {run_idx + 1}: Exception during request: {e}"
                print(f"\n{msg}")
                fail_details.append(msg)
                fails += 1
                continue

            if test["expect_error"]:
                if (r.status_code != 400 or not dicts_equal(data, EXPECTED_ERROR)):
                    msg = (
                        f"[FAIL][{test['name']}] Run {run_idx + 1}: Got status {r.status_code}, response: {data}"
                    )
                    print(f"\n{msg}")
                    fail_details.append(msg)
                    fails += 1
            else:
                if r.status_code != 200 or "recommendations" not in data:
                    msg = (
                        f"[FAIL][{test['name']}] Run {run_idx + 1}: Got status {r.status_code}, response: {data}"
                    )
                    print(f"\n{msg}")
                    fail_details.append(msg)
                    fails += 1
                else:
                    if "expect_len" in test:
                        if len(data["recommendations"]) != test["expect_len"]:
                            msg = (
                                f"[FAIL][{test['name']}] Run {run_idx + 1}: Expected {test['expect_len']} recommendations, got {len(data['recommendations'])}, response: {data}"
                            )
                            print(f"\n{msg}")
                            fail_details.append(msg)
                            fails += 1
                    if test['endpoint'] == "/recommendations/single-activity":
                        for rec in data["recommendations"]:
                            for h in test["payload"].get("recommendationHistory", []):
                                if rec["recommendation"] == h:
                                    msg = (
                                        f"[FAIL][{test['name']}] Run {run_idx + 1}: Recommendation '{h}' from history present in output: {rec}"
                                    )
                                    print(f"\n{msg}")
                                    fail_details.append(msg)
                                    fails += 1
        result_line = f"{test['name']}: {'PASS' if fails == 0 else f'{fails} FAILS'} ({N_RUNS} runs)"
        print(f"  Failed {fails}/{N_RUNS} runs")
        summary_lines.append(result_line)

        # Add fail details to detailed lines if there are any
        if fail_details:
            detailed_lines.append(f"\n--- {test['name']} FAILURES ---")
            detailed_lines.extend(fail_details)

        results.append((test['name'], fails))

    summary_lines.append("\n")
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        for line in summary_lines:
            log_file.write(line + "\n")
        if detailed_lines:
            log_file.write("\n[Failure Details]\n")
            for line in detailed_lines:
                log_file.write(line + "\n")

    print("\n=== SUMMARY ===")
    for name, fails in results:
        print(f"{name}: {'PASS' if fails == 0 else f'{fails} FAILS'}")

    print(f"\nSummary written to {log_file_path}")

if __name__ == "__main__":
    run_tests()
