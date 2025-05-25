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

# --- Imports CrewAI ---
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# --- Imports des schémas et outils ---
from menu_planner.schemas import PaprikaRecipe
from menu_planner.tools.scrapeninja import ScrapeNinjaTool
from crewai_tools import (
    SerperDevTool,
    YoutubeVideoSearchTool,
    SerplyWebSearchTool,
    SerplyNewsSearchTool,
)

# --- Configuration ---
from dotenv import load_dotenv

load_dotenv()

# --- Configuration des outils de recherche ---

# Outils de recherche web et extraction de données
search_tool = SerplyWebSearchTool()           # Recherche web générale
news_tool = SerplyNewsSearchTool()            # Recherche d'actualités culinaires
scrape_tool = ScrapeNinjaTool(                # Extraction web avancée
    geo="fr",                                  # Localisé en France
    timeout=10,                               # Timeout raisonnable pour les sites culinaires
    follow_redirects=1,                        # Suivre les redirections pour les sites complexes
    retry_num=2                                # Réessayer en cas d'échec initial
)
youtube_tool = YoutubeVideoSearchTool()       # Recherche de vidéos de recettes

# Ensemble complet d'outils mis à disposition des agents
search_tools = [
    search_tool,      # Recherche web générale pour les recettes
    news_tool,        # Découverte des tendances culinaires récentes
    scrape_tool,      # Extraction détaillée des sites de recettes
    youtube_tool,     # Tutoriels vidéo pour les techniques culinaires
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

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def recipe_expert(self) -> Agent:
        """
        Agent principal spécialisé dans l'analyse et l'amélioration des recettes.
        
        Cet agent utilise des outils de recherche web pour trouver des informations détaillées
        sur les recettes et les enrichir avec des instructions précises, des informations
        nutritionnelles et des adaptations pour Thermomix.
        
        Capacités:
        - Recherche web avancée de recettes en français
        - Extraction structurée des ingrédients et des étapes
        - Analyse nutritionnelle et calcul de calories
        - Adaptation pour appareils spécifiques
        
        Returns:
            Agent: Instance configurée de l'agent expert en recettes
        """
        return Agent(
            config=self.agents_config["recipe_expert"],
            tools=search_tools,
            verbose=True,
            reasoning=True,            # Capacité de raisonnement améliorée
            max_reasoning_attempts=3,  # Limite pour éviter les boucles infinies
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
