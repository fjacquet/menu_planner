from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel
from typing import List

class IngredientItem(BaseModel):
    name: str
    quantity: float
    unit: str

class CategoryIngredients(BaseModel):
    category: str
    ingredients: List[IngredientItem]

@CrewBase
class ShoppingCrew:
    """ShoppingCrew pour créer une liste de courses organisée à partir des recettes"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def ingredient_organizer(self) -> Agent:
        return Agent(
            config=self.agents_config['ingredient_organizer'],
            verbose=True
        )

    @agent
    def shopping_list_designer(self) -> Agent:
        return Agent(
            config=self.agents_config['shopping_list_designer'],
            verbose=True
        )

    @task
    def aggregate_ingredients(self) -> Task:
        return Task(
            config=self.tasks_config['aggregate_ingredients'],
            verbose=True
        )

    @task
    def organize_by_category(self) -> Task:
        return Task(
            config=self.tasks_config['organize_by_category'],
            verbose=True
        )

    @task
    def create_html_shopping_list(self) -> Task:
        return Task(
            config=self.tasks_config['create_html_shopping_list'],
            output_file="output/shopping_crew/liste_courses.html",
            verbose=True
        )

    @task
    def create_markdown_shopping_list(self) -> Task:
        return Task(
            config=self.tasks_config['create_markdown_shopping_list'],
            output_file="output/shopping_crew/liste_courses.md",
            verbose=True
        )

    @crew
    def crew(self) -> Crew:
        """Crée l'équipe ShoppingCrew pour organiser la liste de courses"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.hierarchical,
            verbose=True,
        )
