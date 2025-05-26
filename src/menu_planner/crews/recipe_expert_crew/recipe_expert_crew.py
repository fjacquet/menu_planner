#!/usr/bin/env python
"""
Recipe Expert Crew - Module spécialisé dans l'analyse et l'enrichissement des recettes

Ce module implémente le crew responsable de la recherche détaillée des recettes,
de leur analyse nutritionnelle, et de leur adaptation pour Thermomix. Il génère
des fichiers structurés HTML, YAML et JSON pour chaque recette du menu.

Author: Fred Jacquet
Version: 1.0.0
License: MIT
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

from menu_planner.tools.safe_serper import SafeSerperTool
from menu_planner.tools.scrapeninja import ScrapeNinjaTool

# Load environment variables
load_dotenv()

# Initialize tools with appropriate configurations
search_tool = SafeSerperTool()  # Recherche web générale avec gestion améliorée des requêtes

scrape_tool = ScrapeNinjaTool(  # Extraction web avancée
    geo="fr",  # Localisé en France
    timeout=10,  # Timeout raisonnable pour les sites culinaires
    follow_redirects=1,  # Suivre les redirections pour les sites complexes
    retry_num=2,  # Réessayer en cas d'échec initial
)

# Ensemble complet d'outils mis à disposition des agents
search_tools = [
    search_tool,  # Recherche web générale pour les recettes
    scrape_tool,  # Extraction détaillée des sites de recettes
]


@CrewBase
class RecipeExpertCrew:
    """
    Crew spécialisé dans l'analyse et l'amélioration des recettes de cuisine.

    Ce crew est responsable de la recherche approfondie d'informations sur chaque
    recette du menu, de son analyse nutritionnelle, et de son adaptation pour
    des appareils spécifiques comme le Thermomix. Il génère plusieurs formats
    de sortie pour chaque recette.

    Le crew utilise des agents spécialisés pour:
    - Rechercher des recettes détaillées avec instructions précises
    - Analyser la valeur nutritionnelle et calculer les calories
    - Adapter les techniques pour l'utilisation du Thermomix
    - Générer des fichiers structurés pour l'affichage et les traitements ultérieurs

    Attributs:
        agents_config: Chemin vers la configuration YAML des agents
        tasks_config: Chemin vers la configuration YAML des tâches
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def culinary_expert(self) -> Agent:
        """
        Agent principal spécialisé dans l'analyse et l'amélioration des recettes.

        Cet agent polyvalent combine la création de recettes, l'adaptation Thermomix
        et l'intégration des améliorations nutritionnelles. Il utilise des outils
        de recherche pour trouver des informations complètes et adapter les recettes
        selon les besoins des familles.

        Capacités:
        - Recherche web avancée de recettes en français
        - Extraction structurée des ingrédients et des étapes
        - Adaptation pour appareils spécifiques (Thermomix)
        - Intégration d'améliorations nutritionnelles

        Returns:
            Agent: Instance configurée de l'agent expert culinaire
        """
        return Agent(
            config=self.agents_config["culinary_expert"],
            tools=search_tools,
            verbose=True,
            reasoning=True,
            max_reasoning_attempts=3,
        )

    @agent
    def nutritionist(self) -> Agent:
        """
        Agent spécialisé dans l'évaluation nutritionnelle des recettes.

        Cet agent analyse les recettes du point de vue nutritionnel
        et propose des améliorations adaptées aux besoins des enfants.

        Returns:
            Agent: Instance configurée de l'agent nutritionniste
        """
        return Agent(
            config=self.agents_config["nutritionist"],
            tools=search_tools,
            verbose=True,
            reasoning=True,
            max_reasoning_attempts=3,
        )
        
    @agent
    def formatting_specialist(self) -> Agent:
        """
        Agent spécialisé dans le formatage des recettes pour différents supports.

        Cet agent génère des formats structurés (HTML, YAML, JSON) à partir
        des recettes développées, en respectant les standards de chaque format
        et les spécifications requises.

        Returns:
            Agent: Instance configurée de l'agent spécialiste en formatage
        """
        return Agent(
            config=self.agents_config["formatting_specialist"],
            tools=search_tools,
            verbose=True,
            reasoning=True,
            max_reasoning_attempts=3,
        )

    @agent
    def content_specialist(self) -> Agent:
        """
        Agent spécialisé dans la création de formats structurés des recettes.

        Cet agent génère des versions attrayantes et bien structurées des recettes
        dans différents formats (HTML, YAML, JSON) adaptés aux besoins spécifiques.

        Returns:
            Agent: Instance configurée de l'agent spécialiste de contenu
        """
        return Agent(
            config=self.agents_config["content_specialist"],
            verbose=True,
            reasoning=True,
        )

    @task
    def recipe_development(self) -> Task:
        """
        Développement complet d'une recette adaptée pour Thermomix avec amélioration nutritionnelle.
        
        Cette tâche combine les étapes de création, adaptation et amélioration nutritionnelle
        en un seul processus intégré pour plus d'efficacité.
        """
        return Task(
            config=self.tasks_config["recipe_development"],
            # Not specifying output_file as this is an intermediate task
            verbose=True
        )

    @task
    def nutrition_evaluation(self) -> Task:
        """
        Évaluation du profil nutritionnel de la recette et suggestions d'amélioration.
        
        Cette tâche fournit une analyse détaillée des aspects nutritionnels et
        propose des modifications adaptées aux besoins des enfants.
        """
        return Task(
            config=self.tasks_config["nutrition_evaluation"],
            # Not specifying output_file as this is an intermediate task
            verbose=True
        )

    @task
    def generate_html(self) -> Task:
        """
        Génération du format HTML pour la recette.
        
        Cette tâche crée une version HTML structurée et élégante de la recette
        pour l'affichage web ou l'impression.
        """
        return Task(
            config=self.tasks_config["generate_html"],
            output_file="{recipe_html_path}",
            verbose=True
        )

    @task
    def generate_yaml(self) -> Task:
        """
        Génération du format YAML pour la recette.
        
        Cette tâche crée une version YAML compatible avec Paprika 3
        pour l'importation dans l'application de gestion de recettes.
        """
        return Task(
            config=self.tasks_config["generate_yaml"],
            output_file="{recipe_yaml_path}",
            verbose=True
        )
        
    @task
    def generate_ingredients_json(self) -> Task:
        """
        Génération du format JSON pour les ingrédients de la recette.
        
        Cette tâche crée une liste structurée des ingrédients au format JSON
        pour faciliter le traitement programmatique et l'analyse.
        """
        return Task(
            config=self.tasks_config["generate_ingredients_json"],
            output_file="{recipe_ingredients_path}",
            verbose=True
        )

    @crew
    def crew(self) -> Crew:
        """
        Configuration du crew avec définition du processus d'exécution.
        
        Returns:
            Crew: Instance complètement configurée du RecipeExpertCrew
        """
        # Define tasks
        recipe_dev = self.recipe_development()
        nutrition = self.nutrition_evaluation()
        html = self.generate_html()
        yaml = self.generate_yaml()
        ingredients = self.generate_ingredients_json()
        
        # Set up task dependencies
        nutrition.context = [recipe_dev]
        html.context = [nutrition]
        yaml.context = [nutrition]
        ingredients.context = [nutrition]
        
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=[recipe_dev, nutrition, html, yaml, ingredients],
            process=Process.sequential,
            respect_context_window=True,
            memory=True,
            cache=True,
            verbose=True,
            timeout=300,
        )
