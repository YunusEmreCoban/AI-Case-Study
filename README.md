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

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```
2. **Set up the virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
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