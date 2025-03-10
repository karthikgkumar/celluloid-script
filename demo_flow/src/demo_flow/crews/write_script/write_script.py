from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI
from src.demo_flow.script_types import Chapter


@CrewBase
class WriteScript:
    """WriteScript Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = ChatOpenAI(model="gpt-4o")

    @agent
    def scene_architect(self) -> Agent:
    
        return Agent(
            config=self.agents_config["scene_architect"],
            llm=self.llm,
            verbose=True,
        )

    @agent
    def dialogue_architect(self) -> Agent:
        return Agent(
            config=self.agents_config["dialogue_architect"],
            llm=self.llm,
            verbose=True,
        )

    @agent
    def format_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["format_manager"],
            llm=self.llm,
            verbose=True,
        )
    @task
    def scene_development_task(self) -> Task:
        return Task(
            config=self.tasks_config["scene_development_task"],
        )
    
    @task
    def dialogue_development_task(self) -> Task:
        return Task(
            config=self.tasks_config["dialogue_development_task"],
        )

    @task
    def format_task(self) -> Task:
        return Task(config=self.tasks_config["format_task"], output_pydantic=Chapter)

    @crew
    def crew(self) -> Crew:
        """Creates the Write Book Chapter Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
