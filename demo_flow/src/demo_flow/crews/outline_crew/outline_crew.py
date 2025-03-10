from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI
from src.demo_flow.script_types import BookOutline
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class OutlineCrew:
    """Script Outline Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = ChatOpenAI(model="gpt-4o-mini")


    @agent
    def outliner(self) -> Agent:
        return Agent(
            config=self.agents_config["outliner"],
            llm=self.llm,
            verbose=True,
        )

    @task
    def outline_creation_task(self) -> Task:
        return Task(
            config=self.tasks_config["outline_creation_task"],
        )

    @task
    def outliner_task(self) -> Task:
        return Task(
            config=self.tasks_config["outliner_task"], output_pydantic=BookOutline
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Script Outline Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
