from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from menu_planner.schemas import MenuJson  # RecipeList handled through the consolidated task
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()

# Initiali
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class MenuDesignerCrew:
    """MenuDesignerCrew crew"""

    # Config file paths relative to this crew module
    agents_config = str(Path(__file__).parent / "config" / "agents.yaml")
    tasks_config = str(Path(__file__).parent / "config" / "tasks.yaml")

    @agent
    def menu_planner_specialist(self) -> Agent:
        """
        Spécialiste en planification de menu qui combine les compétences 
        de recherche et de présentation de menus familiaux.
        
        Cet agent unique gère à la fois la création du menu équilibré
        et sa présentation dans différents formats (JSON, HTML).
        """
        return Agent(
            config=self.agents_config["menu_planner_specialist"],
            verbose=True,
            reasoning=True,
            max_reasoning_attempts=3,
        )

    @task
    def generate_complete_menu_task(self) -> Task:
        """
        Génère simultanément le menu complet et la liste des recettes.
        
        Cette tâche consolidée produit en une seule opération les deux structures
        JSON nécessaires pour le workflow: le menu détaillé et la liste des recettes.
        """
        return Task(
            config=self.tasks_config["generate_complete_menu"],
            output_file="output/menu_designer_crew/menu.json",  # Primary output
            output_json=MenuJson,
            verbose=True,
        )

    @task
    def create_html_presentation_task(self) -> Task:
        """
        Crée une présentation HTML attrayante du menu.
        
        Cette tâche génère un fichier HTML complet à partir des données du menu
        en utilisant un template optimisé pour l'affichage et la lisibilité.
        """
        return Task(
            config=self.tasks_config["create_html_presentation"],
            output_file="output/menu_designer_crew/menu.html",
            verbose=True,
        )

    # @task
    # def send_email_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config["send_email"],
    #         tools=gmail,
    #         verbose=True,
    #     )

    @crew
    def crew(self) -> Crew:
        """Creates the MenuDesignerCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            respect_context_window=True,
            timeout=300,
            process=Process.sequential,
            verbose=True,  # disable crew-level logging to JSON
        )
