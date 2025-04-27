from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from menu_planner.schemas import RecipeList, MenuJson
from composio_crewai import ComposioToolSet, App
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Initialize the toolset
toolset = ComposioToolSet()

search_tools = toolset.get_tools(
    actions=[
        "COMPOSIO_SEARCH_DUCK_DUCK_GO_SEARCH",
        "COMPOSIO_SEARCH_SHOPPING_SEARCH",
        "COMPOSIO_SEARCH_SEARCH",
    ],
)
gmail = toolset.get_tools(apps=[App.GMAIL])

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class MenuDesignerCrew:
    """MenuDesignerCrew crew"""

    # Config file paths relative to this crew module
    agents_config = str(Path(__file__).parent / "config" / "agents.yaml")
    tasks_config = str(Path(__file__).parent / "config" / "tasks.yaml")

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def menu_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["menu_researcher"],
            tools=search_tools,
            verbose=True,
        )

    @agent
    def html_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["html_designer"],
            verbose=True,
        )

    @agent
    def gmail_sender(self) -> Agent:
        return Agent(
            config=self.agents_config["gmail_sender"],
            tools=gmail,
            verbose=True,
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def recherche_menu_task(self) -> Task:
        return Task(
            config=self.tasks_config["recherche_menu"],
            output_file="output/menu_designer_crew/menu.json",
            output_json=MenuJson,
            tools=search_tools,
            verbose=True,
        )

    @task
    def formattage_html_task(self) -> Task:
        return Task(
            config=self.tasks_config["formattage_html"],
            output_file="output/menu_designer_crew/menu.html",
            dependencies=[self.recherche_menu_task],
            verbose=True,
        )

    @task
    def liste_recettes_task(self) -> Task:
        return Task(
            config=self.tasks_config["liste_recettes"],
            output_file="output/menu_designer_crew/liste_recettes.json",
            output_json=RecipeList,
            dependencies=[self.recherche_menu_task],
            verbose=True,
        )

    @task
    def send_email_task(self) -> Task:
        return Task(
            config=self.tasks_config["send_email"],
            tools=gmail,
            verbose=True,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the MenuDesignerCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            manager_llm="gpt-4.1-nano",
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
