#!/usr/bin/env python
"""
Menu Planner - Application de planification de menus mensuels basée sur CrewAI Flow

Ce module implémente l'orchestration complète des différents crews spécialisés pour générer un menu 
familial mensuel, avec liste de courses et poème ludique. Il utilise l'architecture CrewAI Flow pour
organiser le flux de travail entre les différents agents et optimiser le traitement des recettes en parallèle.

Author: Fred Jacquet
Version: 1.0.0
License: MIT
"""

# --- Imports standard et système ---
import os
from random import randint

# --- Imports monitoring et configuration ---
import agentops
from dotenv import load_dotenv

# --- Imports CrewAI ---
from crewai.flow import Flow, and_, listen, router, start

# --- Imports des schemas du projet ---
from menu_planner.schemas import MenuState

# --- Imports des crews spécialisés ---
from menu_planner.crews.poem_crew.poem_crew import PoemCrew
from menu_planner.crews.menu_designer_crew.menu_designer_crew import MenuDesignerCrew
from menu_planner.crews.html_design_crew.html_design_crew import HtmlDesignCrew
from menu_planner.crews.recipe_expert_crew.recipe_expert_crew import RecipeExpertCrew
from menu_planner.crews.shopping_crew.shopping_crew import ShoppingCrew

# --- Configuration ---

# Chargement des variables d'environnement depuis .env
load_dotenv()

# Initialisation du monitoring AgentOps si disponible
if os.getenv("AGENTOPS_API_KEY"):
    agentops.init(
        api_key=os.getenv("AGENTOPS_API_KEY"),
        tags=["crewai", "menu_planner"],
        max_wait_time=5,  # Prévention du blocage sur les requêtes lentes
        max_queue_size=10, # Limite de file d'attente pour la mémoire
    )

# --- Configuration du mode de génération ---

# Pour générer une seule recette, définir le nom ici.
# Pour générer un menu complet, laisser vide.
MaRecette = ""  


class MenuFlow(Flow[MenuState]):
    """
    Orchestration complète du processus de planification de menu familial.
    
    Cette classe implémente le workflow de génération de menu en utilisant CrewAI Flow
    pour coordonner les différents crews spécialisés. Le flux peut générer soit un
    menu mensuel complet, soit une recette spécifique selon la configuration.
    
    Attributs:
        state (MenuState): État global partagé entre les étapes du flow
    """


    @start()
    def generate_sentence_count(self):
        """
        Génère un nombre aléatoire de phrases pour le poème.
        
        Point de départ du flow (@start) pour la génération du poème ludique. Cette méthode
        initialise un nombre aléatoire de phrases pour le poème qui sera généré ensuite.
        
        Returns:
            None: Met à jour self.state.sentence_count avec un nombre aléatoire entre 1 et 5
        """
        print("Generating sentence count")
        self.state.sentence_count = randint(1, 5)

    @listen(generate_sentence_count)
    def generate_poem(self):
        """
        Génère un poème ludique sur le thème de la nutrition.
        
        Déclenchée après generate_sentence_count (@listen), cette méthode utilise
        PoemCrew pour créer un poème adapté à l'âge des enfants avec le nombre de phrases
        défini précédemment. Le poème sera intégré dans la présentation finale du menu.
        
        Returns:
            None: Met à jour self.state.poem avec le poème généré
        """
        print("Generating poem")
        inputs = {
            "sentence_count": self.state.sentence_count,
            "children_age": self.state.children_age,
        }
        result = PoemCrew().crew().kickoff(inputs=inputs)
        print("Poem généré", result.raw)
        self.state.poem = result.raw

    @start()
    def generate_menu(self):
        """
        Génère le menu mensuel complet ou prépare une recette spécifique.
        
        Point de départ principal du flow (@start), cette méthode détermine si nous générons
        un menu complet ou une recette spécifique basée sur la variable globale MaRecette.
        
        Le processus:
        1. Vérifie si une recette spécifique est demandée (MaRecette)
        2. Prépare les variables template requises pour CrewAI
        3. Exécute MenuDesignerCrew pour créer le menu complet
        4. Extrait et stocke les résultats dans l'état partagé
        
        Returns:
            None: Met à jour self.state avec menu_json et recipe_list
        """
        # Si MaRecette est définie, on saute la génération du menu complet
        if MaRecette:
            print(f"Génération d'une recette unique: {MaRecette}")
            self.state.recipe_name = MaRecette
            return

        print("Démarrage de la génération du menu hebdomadaire")
        
        # Initialisation des variables template requises pour CrewAI
        # Ces variables sont nécessaires car elles sont référencées dans les tasks.yaml
        if not hasattr(self.state, 'menu_json') or self.state.menu_json is None:
            self.state.menu_json = {}
            
        if not hasattr(self.state, 'recipe_list') or self.state.recipe_list is None:
            self.state.recipe_list = {"recipes": []}
            
        # Création d'un dictionnaire d'entrées complet pour MenuDesignerCrew
        inputs = {
            # Variables familliales
            "adults": self.state.adults,
            "children": self.state.children,
            "children_age": self.state.children_age,
            
            # Variables template requises (même si initialement vides)
            "menu_json": self.state.menu_json,
            "recipe_list": self.state.recipe_list,
            "send_to": getattr(self.state, 'send_to', ''),
            "menu_html": getattr(self.state, 'menu_html', '')
        }
        
        # Lancement du crew avec toutes les variables requises
        menu_result = MenuDesignerCrew().crew().kickoff(inputs=inputs)
        
        # Mise à jour de l'état avec les résultats générés
        self.state.menu_json = menu_result.get_output(output_key="menu_json")
        self.state.recipe_list = menu_result.get_output(output_key="recipe_list")

    @router(generate_menu)
    def route_menu_or_recipe(self):
        if MaRecette:
            return self.generate_single_recipe
        else:
            return self.check_state

    @listen(route_menu_or_recipe)
    def generate_single_recipe(self):
        if MaRecette != "":
            print(f"Génération de la recette: {self.state.recipe_name}")
            inputs = {
                "recipe_name": self.state.recipe_name,
                "recipe_id": self.state.recipe_name.lower().replace(" ", "_"),
                "recipe_html_path": f"output/recipe_expert_crew/{self.state.recipe_name.lower().replace(" ", "_")}.html",
                "recipe_yaml_path": f"output/recipe_expert_crew/{self.state.recipe_name.lower().replace(" ", "_")}.yaml",
                "recipe_ingredients_path": f"output/recipe_expert_crew/{self.state.recipe_name.lower().replace(" ", "_")}_ingredients.json",
                "menu_json": self.state.menu_json,
            }
            RecipeExpertCrew().crew().kickoff(inputs=inputs)
            print(f"Recette générée: {self.state.recipe_name}")

    @router(and_("generate_menu", "generate_poem"))
    def check_state(self):
        recipes = self.state.recipe_list
        print("Recipes", recipes)
        # Menu used in subsequent steps
        return self.insert_poem

    @listen(check_state)
    def insert_poem(self):
        inputs = {
            "menu_json": self.state.menu_json.model_dump() if self.state.menu_json else None,
            "recipe_list": self.state.recipe_list.model_dump() if self.state.recipe_list else None,
            "poem": self.state.poem,
        }
        HtmlDesignCrew().crew().kickoff(inputs=inputs)

    @listen(insert_poem)
    def prepare_recipes(self):
        """
        Traite en parallèle toutes les recettes du menu avec kickoff_for_each.
        
        Cette méthode est un point d'optimisation clé de l'application, permettant 
        le traitement concurrent de multiples recettes en utilisant la fonction 
        kickoff_for_each de CrewAI. Cela accélère considérablement l'exécution 
        comparé au traitement séquentiel traditionnel.
        
        Processus:
        1. Prépare des entrées pour chaque recette avec chemins standardisés
        2. Utilise crew.kickoff_for_each pour traitement parallèle efficace
        3. Suit l'avancement et capture les résultats pour chaque recette
        4. Gère les erreurs avec un fallback séquentiel si nécessaire
        
        Args:
            self: Instance de MenuFlow avec l'état partagé
            
        Returns:
            None: Met à jour self.state avec les chemins des fichiers générés
        """
        recipe_list = self.state.recipe_list
        
        # Initialisation des listes de suivi pour les fichiers générés
        # Ces informations seront utilisées par shopping_crew ensuite
        self.state.recipe_ids = []
        self.state.recipe_htmls = []
        self.state.recipe_yamls = []
        self.state.recipe_ingredients_files = []
        
        if not recipe_list:
            print("No recipes found.")
            return
        
        # Préparation des données d'entrée pour le traitement parallèle
        recipe_inputs = []
        for recipe_name in recipe_list.recipes:
            # Normalisation des noms de fichiers
            recipe_id = recipe_name.lower().replace(" ", "_")
            
            # Définition des chemins de fichiers de sortie standardisés
            recipe_html = f"output/recipe_expert_crew/{recipe_id}.html"
            recipe_yaml = f"output/recipe_expert_crew/{recipe_id}.yaml"
            recipe_ingredients = f"output/recipe_expert_crew/{recipe_id}_ingredients.json"
            
            # Création du dictionnaire d'entrée pour chaque recette
            recipe_inputs.append({
                # Paramètres pour RecipeExpertCrew
                "recipe_name": recipe_name,
                "recipe_id": recipe_id,
                "recipe_html_path": recipe_html,
                "recipe_yaml_path": recipe_yaml,
                "recipe_ingredients_path": recipe_ingredients,
                "menu_json": self.state.menu_json,
                
                # Métadonnées pour suivi des fichiers générés
                "_tracking": {
                    "id": recipe_id,
                    "html": recipe_html,
                    "yaml": recipe_yaml,
                    "ingredients": recipe_ingredients
                }
            })
        
        # Process recipes in parallel with crew.kickoff_for_each
        print(f"Processing {len(recipe_inputs)} recipes in parallel...")
        crew = RecipeExpertCrew().crew()
        
        try:
            # Use crew.kickoff_for_each to process recipes in parallel
            results = crew.kickoff_for_each(inputs=recipe_inputs)
            print(f"Parallel processing complete. Got {len(results)} results.")
            
            # Process results and update state
            successful_recipes = 0
            for i, result in enumerate(results):
                if result is not None:  # Successfully processed
                    input_data = recipe_inputs[i]
                    tracking = input_data["_tracking"]
                    self.state.recipe_ids.append(tracking["id"])
                    self.state.recipe_htmls.append(tracking["html"])
                    self.state.recipe_yamls.append(tracking["yaml"])
                    self.state.recipe_ingredients_files.append(tracking["ingredients"])
                    successful_recipes += 1
                    print(f"✓ Successfully processed recipe: {input_data['recipe_name']}")
                else:
                    print(f"✗ Failed to process recipe: {recipe_inputs[i]['recipe_name']}")
            
            print(f"Processed {successful_recipes}/{len(recipe_inputs)} recipes successfully")
            
        except Exception as e:
            print(f"Error in parallel recipe processing: {e}")
            # Fallback to sequential processing if parallel fails
            print("Falling back to sequential processing...")
            
            successful_recipes = 0
            for input_data in recipe_inputs:
                try:
                    result = crew.kickoff(inputs=input_data)
                    tracking = input_data["_tracking"]
                    self.state.recipe_ids.append(tracking["id"])
                    self.state.recipe_htmls.append(tracking["html"])
                    self.state.recipe_yamls.append(tracking["yaml"])
                    self.state.recipe_ingredients_files.append(tracking["ingredients"])
                    successful_recipes += 1
                    print(f"✓ Successfully processed: {input_data['recipe_name']}")
                except Exception as e:
                    print(f"✗ Error processing recipe {input_data['recipe_name']}: {e}")
            
            print(f"Processed {successful_recipes}/{len(recipe_inputs)} recipes successfully (sequential fallback)")

    @listen(prepare_recipes)
    def prepare_shopping_list(self):
        ShoppingCrew().crew().kickoff(
            inputs={
                "recipe_list": self.state.recipe_list.model_dump() if self.state.recipe_list else None,
                "adults": self.state.adults,
                "children": self.state.children,
                "children_age": self.state.children_age,
                "poem": self.state.poem,
                "recipe_ids": self.state.recipe_ids,
                "recipe_htmls": self.state.recipe_htmls,
                "recipe_yamls": self.state.recipe_yamls,
                "recipe_ingredients_files": self.state.recipe_ingredients_files
            }
        )

def kickoff():
    menu_flow = MenuFlow()
    menu_flow.kickoff()


def plot():
    menu_flow = MenuFlow()
    menu_flow.plot()


if __name__ == "__main__":
    kickoff()
