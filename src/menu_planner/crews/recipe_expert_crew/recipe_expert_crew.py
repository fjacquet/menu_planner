from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from composio_crewai import ComposioToolSet, App, Action
from menu_planner.schemas import RecipeIngredient, RecipeOutput, PaprikaRecipe
from dotenv import load_dotenv

load_dotenv()

# Initialize the toolset
toolset = ComposioToolSet()

search_tools = toolset.get_tools(
    actions=[
        "COMPOSIO_SEARCH_DUCK_DUCK_GO_SEARCH",
        'COMPOSIO_SEARCH_SEARCH',
    ],
)



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
            verbose=True
        )

    @agent
    def thermomix_adapter(self) -> Agent:
        return Agent(
            config=self.agents_config["thermomix_adapter"],
            tools=search_tools,
            verbose=True,
        )

    @agent
    def nutritionist(self) -> Agent:
        return Agent(
            config=self.agents_config["nutritionist"],
            tools=search_tools, 
            verbose=True
        )


    def cook_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['cook_manager'],
            verbose=True
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
            dependencies=[self.recipe_creation],
            verbose=True,
        )

    @task
    def nutrition_evaluation(self) -> Task:
        return Task(
            config=self.tasks_config['nutrition_evaluation'],
            dependencies=[self.thermomix_adaptation],
            verbose=True,
        )

    @task
    def recipe_integration(self) -> Task:
        return Task(
            config=self.tasks_config['recipe_integration'],
            dependencies=[self.nutrition_evaluation],
            verbose=True,
        )

    # @task
    # def recipe_validation(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['recipe_validation'],
    #         dependencies=[self.recipe_integration],
    #         verbose=True
    #     )

    @task
    def html_creation(self) -> Task:
        return Task(
            config=self.tasks_config["html_creation"],
            dependencies=[self.recipe_integration],
            verbose=True,
        )

    @task
    def paprika_creation(self) -> Task:
        return Task(
            config=self.tasks_config["paprika_creation"],
            dependencies=[self.recipe_integration],
            output_json=PaprikaRecipe,
            verbose=True,
        )

    @task
    def ingredient_list(self) -> Task:
        return Task(
            config=self.tasks_config["ingredient_list"],
            dependencies=[self.recipe_integration],
            verbose=True,
        )

    @crew
    def crew(self) -> Crew:
        """Crée le RecipeExpertCrew pour traiter les recettes"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            manager_llm="gpt-4.1-nano",
            verbose=True,
        )
