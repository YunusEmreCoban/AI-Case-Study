from typing import List
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.tasks.conditional_task import ConditionalTask

from crews.crew_multi import has_candidates
from crews.crew_utils import azure_llm_provider
    
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
        return Agent(config=self.agents_config["matcher"], allow_delegation=False, llm=azure_llm_provider())

    @agent
    def ranker(self) -> Agent:
        """Agent: Rank selected candidates. Based on impactLevel and feasibilityLevel"""
        return Agent(config=self.agents_config["ranker"], allow_delegation=False, llm=azure_llm_provider())

    def fetch_candidates_single_task(self) -> Task:
        """Task: Fetch candidates matching the single-activity criteria."""
        return Task(config=self.tasks_config["fetch_candidates_single_task"], 
                               agent=self.matcher())

    def rank_and_select_task(self) -> Task:
        """Task: Conditionally rank and select top recommendations."""
        return ConditionalTask(config=self.tasks_config["rank_and_select_task"], 
                               agent=self.ranker(),
                               condition=has_candidates)



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
