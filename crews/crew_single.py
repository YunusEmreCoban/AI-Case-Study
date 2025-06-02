import json
from typing import List
from crewai import Agent, Task, Crew, Process, TaskOutput
from crewai.project import CrewBase, agent, task, crew
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.tasks.conditional_task import ConditionalTask


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

    
@CrewBase
class SingleRecommendationCrew:
    """
    Crew pipeline for generating and ranking single-activity recommendations.

    Loads agent and task configs from YAML files.
    Workflow:
      1. matcher agent fetches candidates. matcher also checking the history.
      2. ranker agent ranks candidates (if any).

    ConditionalTask used for interrupting workflow.
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def matcher(self) -> Agent:
        """Agent: Fetch candidate recommendations for id and name matching"""
        return Agent(config=self.agents_config["matcher"], allow_delegation=False)

    @agent
    def ranker(self) -> Agent:
        """Agent: Rank selected candidates. Based on impactLevel and feasibilityLevel"""
        return Agent(config=self.agents_config["ranker"], allow_delegation=False, memory=True)

    def fetch_candidates_single_task(self) -> Task:
        """Task: Fetch candidates matching the single-activity criteria."""
        return Task(config=self.tasks_config["fetch_candidates_single_task"], 
                               agent=self.matcher())

    def rank_and_select_task(self) -> Task:
        """Task: Conditionally rank and select top recommendations."""
        return ConditionalTask(
            description="Rank and select top recommendations.",
            agent=self.ranker(),
            expected_output="Top-ranked recommendations.",
            condition=has_candidates
        )


    @crew
    def single_crew(self) -> Crew:
        return Crew(
            # https://docs.crewai.com/concepts/crews
            # Tasks and Agents automatically collected by the @agent and @task decorator but
            # The conditional task pipeline need to define differently
            # see https://docs.crewai.com/learn/conditional-tasks
            agents=self.agents,
            tasks=[self.fetch_candidates_single_task(),self.rank_and_select_task()],
            process=Process.sequential,
            verbose=True
        )
