# AI Agent Case Study – Multi-Agent Recommendation System (CrewAI)

This project is a FastAPI-powered API that uses [CrewAI](https://github.com/joaomdmoura/crewai) to orchestrate multiple agents that collaboratively generate and rank sustainability-related activity recommendations.

---

## ⚙️ Features

- 🔁 **Two endpoints**: `/recommendations/multi-activity` and `/recommendations/single-activity` recommendation flows.
- 🧠 **Agent-driven logic**: Matcher and Ranker agents built using YAML config.
- 📄 **Well-structured API** with pydantic request/response validation.
- 🧪 **Extensive testing**: Covers edge cases, failure modes, and hallucination checks.

---

<p align="center">
  <b>Workflow Diagram</b><br><br>
  <img src="https://i.ibb.co/KzRSjfn8/diagram-export-6-2-2025-5-19-04-PM.png" alt="System Workflow" width="750">
</p>

#### Link for Diagram: https://i.ibb.co/KzRSjfn8/diagram-export-6-2-2025-5-19-04-PM.png
---
## 📁 Project Structure

```bash
.
├── crews/                         # Contains CrewAI logic for multi/single flows
├── data/                          # Static data files (e.g., recommendations)
├── test_logs/                     # Logs of test input/output results
├── .gitignore                     # Ignores virtual envs, caches, etc.
├── main.py                        # FastAPI application entrypoint
├── models.py                      # Pydantic request/response models
├── requirements.txt               # Python dependencies
├── service.py                     # Core service layer for API logic
├── test_multi_activity.py         # Test for multi-activity endpoint
├── test_recommendation_api.py     # Hallucination and stress testing
├── test_single_activity.py        # Test for single-activity endpoint
```
---
## 🛠️ How It Works

This project uses a multi-agent architecture powered by [CrewAI](https://github.com/joaomdmoura/crewai), wrapped in a FastAPI service to deliver intelligent activity recommendations.


### 🔄 Step-by-Step Workflow

1. **User sends a POST request** to:
   - `/recommendations/multi-activity` – for multiple activities
   - `/recommendations/single-activity` – for one activity

2. **FastAPI receives the request** and validates it using Pydantic models.

3. The request is routed to the appropriate service:
   - `multi_activity_service()` or `single_activity_service()`

4. The service loads mock data from `data/dummy_recommendations.json`.

5. **CrewAI pipeline kicks off**:
   - `matcher` agent finds candidate recommendations.
   - If `matcher` returns results:
     - `ranker` agent ranks them based on impact and feasibility.
   - If `matcher` fails or returns nothing:
     - API returns an `ERR_NO_ACTIVITY` error response.

6. **Final recommendations are returned** to the client in structured JSON format.

---

### 🧠 Agents Involved

- **Matcher Agent**  
  Finds possible recommendations that match the activity name and ID.

- **Ranker Agent**  
  Sorts recommendations based on:
  - `impactLevel`
  - `feasibilityLevel`

---

### ⚙️ Config-Driven

Agent behavior and task flow are configured via YAML:
- `config/agents.yaml` – matcher and ranker setup
- `config/tasks.yaml` – task logic

---

---
## 🚀 Installation
Ensure you have Python >=3.10 <3.13 installed on your system for crewai.
1. **Clone the repository**
```bash

git clone https://github.com/YunusEmreCoban/AI-Case-Study.git
cd AI-Case-Study

```
2. **Set up the virtual environment**
```bash
python -m venv venv
venv\Scripts\activate #On Windows
source venv/bin/activate #On Mac/Linux
```
3. **Install dependencies bash Copy Edit**
```bash
pip install -r requirements.txt
```
4. **Set your OpenAI API key**
```bash
set OPENAI_API_KEY=sk-x #On Windows
export OPENAI_API_KEY=sk-x  #On Linux
```
---
## ▶️ Running the API

**Deploying API**
```bash
uvicorn main:app --reload
```
**Endpoint will be:  http://localhost:8000/ for API **
If you have problem with deploying on Mac/Linux try this command:
```bash
./venv/bin/uvicorn main:app --reload
```

---
## 📬 API Endpoints

### `POST /recommendations/multi-activity`
Generate recommendations based on a list of activities.

### `POST /recommendations/single-activity`
Generate recommendations for a single activity, considering history.

---

### 🔁 Common error response
```json
{
  "error": {
    "code": "ERR_NO_ACTIVITY",
    "message": "No activity found for analysis."
  }
}
```

---

## 🧪 Testing

Three main test files exist:

- `test_recommendation_api.py`: Repeats test cases to detect hallucinations.
- `test_multi_activity.py`: Standalone test for multi-activity flow.
- `test_single_activity.py`: Standalone test for single-activity flow.

Each test logs inputs and outputs to the `test_logs/` directory.

### Run an example test:

```bash
python test_multi_activity.py

```
---
## 🧪 Quick Test with curl

You can test the API directly using `curl` commands below.

---

### 🔹 Multi-Activity Request

💻 Windows (Command Prompt / PowerShell)

```bash
curl -X POST http://127.0.0.1:8000/recommendations/multi-activity ^
  -H "Content-Type: application/json" ^
  -d "{\"scope\":\"1.1\",\"scopeName\":\"Stationary Combustion\",\"maxRecommendationAmount\":2,\"activities\":[{\"id\":\"uuid-1\",\"name\":\"Natural Gas\"},{\"id\":\"uuid-2\",\"name\":\"Diesel\"},{\"id\":\"uuid-3\",\"name\":\"Diesel\"}],\"organizationId\":\"dummy-org-id\"}"
```
🐧 Linux / macOS

```bash
curl -X POST http://127.0.0.1:8000/recommendations/multi-activity \
  -H "Content-Type: application/json" \
  -d '{"scope":"1.1","scopeName":"Stationary Combustion","maxRecommendationAmount":2,"activities":[{"id":"uuid-1","name":"Natural Gas"},{"id":"uuid-2","name":"Diesel"},{"id":"uuid-3","name":"Diesel"}],"organizationId":"dummy-org-id"}'
```

---

### 🔹 Single-Activity Request
💻 Windows (Command Prompt / PowerShell)

```bash
curl -X POST http://127.0.0.1:8000/recommendations/single-activity ^
  -H "Content-Type: application/json" ^
  -d "{\"scope\":\"1.1\",\"scopeName\":\"Stationary Combustion\",\"recommendationAmount\":2,\"activityId\":\"uuid-2\",\"activityName\":\"Diesel\",\"organizationId\":\"dummy-org-id\",\"recommendationHistory\":[\"Conduct staff training on eco-driving\"]}"
```


🐧 Linux / macOS

```bash
curl -X POST http://127.0.0.1:8000/recommendations/single-activity \
  -H "Content-Type: application/json" \
  -d '{"scope":"1.1","scopeName":"Stationary Combustion","recommendationAmount":2,"activityId":"uuid-2","activityName":"Diesel","organizationId":"dummy-org-id","recommendationHistory":["Conduct staff training on eco-driving"]}'

```