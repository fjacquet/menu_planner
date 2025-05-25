from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from menu_planner.schemas import PaprikaRecipe
from menu_planner.tools.scrapeninja import ScrapeNinjaTool
from crewai_tools import (
    SerperDevTool,
    YoutubeVideoSearchTool,
    SerplyWebSearchTool,
    SerplyNewsSearchTool,
)



from dotenv import load_dotenv

load_dotenv()

# Initialize the toolset
# toolset = ComposioToolSet()

search_tool = SerplyWebSearchTool()
news_tool = SerplyNewsSearchTool()
scrape_tool = ScrapeNinjaTool(geo="fr", timeout=10, follow_redirects=1, retry_num=2)
youtube_tool = YoutubeVideoSearchTool()

# Les instruments sacrés de révélation de la sagesse touristique
search_tools = [
    search_tool,  # Le bâton d'Aaron - qui fleurit de connaissances
    news_tool,
    scrape_tool,  # La manne céleste - nourrissant de données
    youtube_tool,  # Les vidéos sacrées - révélateur d'informations
]

@CrewBase
class RecipeExpertCrew:
    """RecipeExpertCrew - Crew spécialisé dans la création et l'amélioration de recettes"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def recipe_expert(self) -> Agent:
        return Agent(
            config=self.agents_config["recipe_expert"],
            tools=search_tools,
            verbose=True,
            reasoning=True,
            max_reasoning_attempts=3,  # Optional: Set a limit on reasoning attempts
        )

    @agent
    def thermomix_adapter(self) -> Agent:
        return Agent(
            config=self.agents_config["thermomix_adapter"],
            tools=search_tools,
            reasoning=True,
            max_reasoning_attempts=3, 
            verbose=True,
        )

    @agent
    def nutritionist(self) -> Agent:
        return Agent(
            config=self.agents_config["nutritionist"],
            tools=search_tools,
            verbose=True,
            reasoning=True,
            max_reasoning_attempts=3,
        )


    def cook_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["cook_manager"],
            verbose=True,
            reasoning=True,
            max_reasoning_attempts=3,
        )

    @agent
    def specialized_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['specialized_writer'],
            verbose=True
        )

    @task
    def recipe_creation(self) -> Task:
        return Task(
            config=self.tasks_config['recipe_creation'],
            verbose=True
        )

    @task
    def thermomix_adaptation(self) -> Task:
        return Task(
            config=self.tasks_config['thermomix_adaptation'],
            verbose=True,
        )

    @task
    def nutrition_evaluation(self) -> Task:
        return Task(
            config=self.tasks_config['nutrition_evaluation'],
            verbose=True,
        )

    @task
    def recipe_integration(self) -> Task:
        return Task(
            config=self.tasks_config['recipe_integration'],
            verbose=True,
        )

    @task
    def html_creation(self) -> Task:
        return Task(
            config=self.tasks_config["html_creation"],
            verbose=True,
        )

    @task
    def paprika_creation(self) -> Task:
        return Task(
            config=self.tasks_config["paprika_creation"],
            verbose=True,
        )

    @task
    def ingredient_list(self) -> Task:
        return Task(
            config=self.tasks_config["ingredient_list"],
            verbose=True,
        )

    @crew
    def crew(self) -> Crew:
        """Crée le RecipeExpertCrew pour traiter les recettes"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.hierarchical,
            respect_context_window=True,
            cache=True,
            verbose=True,
            memory=True,
            planning=True,
            timeout=300,
            manager_llm="ollama/gemma3:latest",
        )
