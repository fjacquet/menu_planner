from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class HtmlDesignCrew:
    """HtmlDesignCrew for professional French menu HTML generation"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'],
            verbose=True
        )

    @task
    def html_menu_task(self) -> Task:
        return Task(
            config=self.tasks_config['html_menu_task'],
            output_file='output/menu_designer_crew/menu.html',
            verbose=True,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
