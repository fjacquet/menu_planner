#!/usr/bin/env python
"""
# --- Menu Planner ---
# Application de planification de menus pour familles
# Propulsée par CrewAI Flow pour orchestration multi-agents optimisée
# Développée par Frédéric Jacquet

# Cette application utilise une architecture Flow de CrewAI pour générer
# et gérer un menu hebdomadaire complet. Chaque étape du processus est 
# gérée par des crews spécialisés optimisés pour leurs tâches spécifiques.

# Pour plus d'informations, consultez la documentation dans README.md
"""

# --- Imports standard et système ---
import os
import json
import logging
from pathlib import Path

# --- Imports monitoring et configuration ---
import agentops
from dotenv import load_dotenv

# --- Imports du framework CrewAI ---
from crewai.flow import Flow, start, listen, router, and_

# --- Imports des schemas ---
from menu_planner.schemas import MenuState
from menu_planner.config import config

# --- Imports des crews spécialisés ---
from menu_planner.crews.menu_designer_crew.menu_designer_crew import MenuDesignerCrew
from menu_planner.crews.html_design_crew.html_design_crew import HtmlDesignCrew
from menu_planner.crews.recipe_expert_crew.recipe_expert_crew import RecipeExpertCrew
from menu_planner.crews.shopping_crew.shopping_crew import ShoppingCrew

# Initialiser le logging
logging.basicConfig(
    level=logging.DEBUG if config.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("menu_planner")

load_dotenv()  # Chargement des variables d'environnement

# Initialisation du monitoring si la clé API est définie
if os.getenv("AGENTOPS_API_KEY"):
    logger.info("Initializing AgentOps monitoring")
    agentops.init(
        api_key=os.getenv("AGENTOPS_API_KEY"),
    )

# Créer les dossiers de sortie s'ils n'existent pas
output_dirs = [
    "output/menu_designer_crew",
    "output/recipe_expert_crew",
    "output/shopping_crew",
    "output/html_design_crew"
]

for directory in output_dirs:
    Path(directory).mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured output directory exists: {directory}")

# Configuration pour le mode de génération (une recette ou menu complet)
# Pour générer une seule recette, définir le nom ici.
# Pour générer un menu complet, laisser vide.
MaRecette = config.single_recipe if hasattr(config, 'single_recipe') else ""
logger.info(f"Recipe generation mode: {'Single recipe: ' + MaRecette if MaRecette else 'Full menu'}")


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
            logger.info(f"Génération d'une recette unique: {MaRecette}")
            self.state.recipe_name = MaRecette
            return

        logger.info("Démarrage de la génération du menu hebdomadaire")
        
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
        logger.info("Starting MenuDesignerCrew to generate weekly menu")
        try:
            menu_designer_crew = MenuDesignerCrew()
            menu_result = menu_designer_crew.crew().kickoff(inputs=inputs)
            
            # Use standard CrewAI output handling pattern - direct task attribute access
            logger.debug(f"Menu result type: {type(menu_result)}")
            
            # Get menu_json from recherche_menu_task result
            try:
                self.state.menu_json = menu_result.recherche_menu
                logger.info("Successfully extracted menu_json from recherche_menu task")
            except AttributeError:
                try:
                    # Try task output with the actual task name
                    self.state.menu_json = menu_result.recherche_menu_task
                    logger.info("Successfully extracted menu_json from recherche_menu_task attribute")
                except AttributeError:
                    # Fallback for older CrewAI versions
                    if hasattr(menu_result, 'raw') and isinstance(menu_result.raw, dict) and 'menu_json' in menu_result.raw:
                        self.state.menu_json = menu_result.raw['menu_json']
                        logger.info("Extracted menu_json from raw dictionary output")
                    else:
                        logger.warning("Could not extract menu_json, initializing empty structure")
                        self.state.menu_json = {}
            
            # Get recipe_list from liste_recettes_task result
            try:
                self.state.recipe_list = menu_result.liste_recettes
                logger.info("Successfully extracted recipe_list from liste_recettes task")
            except AttributeError:
                try:
                    # Try task output with the actual task name
                    self.state.recipe_list = menu_result.liste_recettes_task
                    logger.info("Successfully extracted recipe_list from liste_recettes_task attribute")
                except AttributeError:
                    # Fallback for older CrewAI versions
                    if hasattr(menu_result, 'raw') and isinstance(menu_result.raw, dict) and 'recipe_list' in menu_result.raw:
                        self.state.recipe_list = menu_result.raw['recipe_list']
                        logger.info("Extracted recipe_list from raw dictionary output")
                    else:
                        # Final fallback: try to extract from other MenuDesignerCrew output files
                        try:
                            import json
                            with open("output/menu_designer_crew/liste_recettes.json", 'r') as f:
                                self.state.recipe_list = json.load(f)
                            logger.info("Extracted recipe_list from output file")
                        except (FileNotFoundError, json.JSONDecodeError) as e:
                            logger.warning(f"Could not load recipe list from file: {str(e)}")
                            logger.warning("Could not extract recipe_list, initializing empty structure")
                            self.state.recipe_list = {"recipes": []}
                        
            # Log successful menu generation
            logger.info(f"Successfully generated menu with {len(self.state.recipe_list.get('recipes', []))} recipes")
            
        except Exception as e:
            logger.error(f"Error in MenuDesignerCrew execution: {str(e)}")
            # Initialize empty structures if an error occurred
            if not hasattr(self.state, 'menu_json') or not self.state.menu_json:
                self.state.menu_json = {}
            if not hasattr(self.state, 'recipe_list') or not self.state.recipe_list:
                self.state.recipe_list = {"recipes": []}

    @router(generate_menu)
    def route_menu_or_recipe(self):
        """
        Route vers la génération d'une recette unique ou d'un menu complet.
        
        Cette méthode détermine le flux d'exécution en fonction de la valeur de MaRecette.
        Si MaRecette est défini, elle redirige vers la génération d'une recette unique,
        sinon vers la vérification de l'état pour continuer le traitement du menu complet.
        
        Returns:
            Callable: La méthode suivante à exécuter dans le flux
        """
        if MaRecette:
            logger.info("Routing to single recipe generation")
            return self.generate_single_recipe
        else:
            logger.info("Routing to full menu processing")
            return self.check_state

    @listen(route_menu_or_recipe)
    def generate_single_recipe(self):
        """
        Génère une recette unique spécifiée par MaRecette.
        
        Cette méthode prépare les chemins de fichiers standardisés pour la recette demandée
        et appelle RecipeExpertCrew pour générer la recette et ses détails.
        
        Returns:
            None: Génère les fichiers de recette spécifiés dans les chemins
        """
        if MaRecette != "":
            logger.info(f"Génération de la recette unique: {self.state.recipe_name}")
            recipe_id = self.state.recipe_name.lower().replace(" ", "_")
            
            # Préparer les chemins standardisés pour les fichiers de sortie
            inputs = {
                "recipe_name": self.state.recipe_name,
                "recipe_id": recipe_id,
                "recipe_html_path": f"output/recipe_expert_crew/{recipe_id}.html",
                "recipe_yaml_path": f"output/recipe_expert_crew/{recipe_id}.yaml",
                "recipe_ingredients_path": f"output/recipe_expert_crew/{recipe_id}_ingredients.json",
                "menu_json": self.state.menu_json or {},
            }
            
            try:
                # Lancer la génération de recette
                recipe_expert_crew = RecipeExpertCrew()
                result = recipe_expert_crew.crew().kickoff(inputs=inputs)
                
                # Accès aux résultats selon les conventions CrewAI
                logger.debug(f"Recipe generation result type: {type(result)}")
                logger.info(f"Recette générée avec succès: {self.state.recipe_name}")
                
            except Exception as e:
                logger.error(f"Erreur lors de la génération de la recette {self.state.recipe_name}: {str(e)}")

    @router(and_("generate_menu"))
    def check_state(self):
        """
        Vérifie l'état du menu et transmet le flux vers la préparation des recettes.
        
        Cette méthode vérifie que le menu contient des recettes et log leur nombre
        avant de continuer vers la préparation des recettes.
        
        Returns:
            Callable: La méthode prepare_recipes à exécuter ensuite
        """
        # Simple check for recipe list
        if not self.state.recipe_list:
            logger.warning("Recipe list is empty or missing")
            return self.prepare_recipes
        
        # Ensure recipe_list is in expected format
        if isinstance(self.state.recipe_list, list):
            # Convert list to standard format
            self.state.recipe_list = {"recipes": self.state.recipe_list}
            logger.info("Converted recipe list from list to dict format")
            
        # Check for recipes key in dictionary
        if isinstance(self.state.recipe_list, dict) and "recipes" in self.state.recipe_list:
            recipes_count = len(self.state.recipe_list["recipes"])
            logger.info(f"Found {recipes_count} recipes in menu")
        else:
            logger.warning("Recipe list does not contain expected 'recipes' key")
            # Initialize empty recipe list to avoid errors
            self.state.recipe_list = {"recipes": []}
            
        # Continuer vers la préparation des recettes
        return self.prepare_recipe_inputs

    @listen(check_state)
    def prepare_recipe_inputs(self):
        """
        Prépare les entrées standardisées pour le traitement des recettes.
        
        Cette méthode extrait les recettes du menu (depuis l'état ou le fichier)
        et prépare les structures d'entrée avec des chemins de fichiers standardisés.
        
        Returns:
            Callable: La méthode suivante à exécuter dans le flux
        """
        menu_data = None
        
        # Try to get menu data from state
        if hasattr(self.state, 'menu_json') and self.state.menu_json:
            menu_data = self.state.menu_json
            logger.info("Menu data loaded from state")
        # Try to load from file if not in state
        else:
            menu_file = "output/menu_designer_crew/menu.json"
            if os.path.exists(menu_file):
                try:
                    with open(menu_file, 'r', encoding='utf-8') as f:
                        menu_data = json.load(f)
                        logger.info(f"Menu data loaded from {menu_file}")
                except Exception as e:
                    logger.error(f"Failed to load menu from {menu_file}: {str(e)}")
        
        if not menu_data:
            logger.error("Aucune donnée de menu trouvée dans l'état ou le fichier")
            return self.route_after_recipes
            
        # Extract all unique recipes from the menu
        all_recipes = []
        
        # Extract all recipes from the menu
        for day, meals in menu_data.get("menu", {}).items():
            for meal_type, meal in meals.items():
                if meal and "title" in meal and meal["title"]:
                    all_recipes.append(meal["title"])
        
        # Remove duplicates while preserving order
        unique_recipes = []
        seen = set()
        for recipe in all_recipes:
            if recipe not in seen:
                seen.add(recipe)
                unique_recipes.append(recipe)
        
        # Update recipe_list in state to match the menu
        self.state.recipe_list = {"recipes": unique_recipes}
        
        # Save the updated recipe list to file
        with open("output/menu_designer_crew/liste_recettes.json", "w", encoding="utf-8") as f:
            json.dump({"recipes": unique_recipes}, f, ensure_ascii=False, indent=2)
        
        if not unique_recipes:
            logger.warning("Aucune recette à traiter dans le menu")
            return self.route_after_recipes
            
        logger.info(f"Préparation de {len(unique_recipes)} recettes uniques à partir du menu")

        # Initialize tracking for recipe files
        self.state.recipe_ids = []
        self.state.recipe_htmls = []
        self.state.recipe_yamls = []
        self.state.recipe_ingredients_files = []
        
        # Prepare input list for processing
        recipe_inputs = []
        
        for recipe_name in unique_recipes:
            # Prepare standardized file paths
            recipe_id = recipe_name.lower().replace(" ", "_").replace("'", "").replace("é", "e").replace("è", "e")
            recipe_html_path = f"output/recipe_expert_crew/{recipe_id}.html"
            recipe_yaml_path = f"output/recipe_expert_crew/{recipe_id}.yaml"
            recipe_ingredients_path = f"output/recipe_expert_crew/{recipe_id}_ingredients.json"
            
            # Add to state tracking
            self.state.recipe_ids.append(recipe_id)
            self.state.recipe_htmls.append(recipe_html_path)
            self.state.recipe_yamls.append(recipe_yaml_path)
            self.state.recipe_ingredients_files.append(recipe_ingredients_path)
            
            # Prepare input for recipe processing
            recipe_input = {
                "recipe_name": recipe_name,
                "recipe_id": recipe_id,
                "recipe_html_path": recipe_html_path,
                "recipe_yaml_path": recipe_yaml_path,
                "recipe_ingredients_path": recipe_ingredients_path,
                "adults": getattr(self.state, 'adults', config.family.adults),
                "children": getattr(self.state, 'children', config.family.children),
                "children_age": getattr(self.state, 'children_age', config.family.children_age),
            }
            recipe_inputs.append(recipe_input)
            
            logger.debug(f"Préparé la recette: {recipe_name} (ID: {recipe_id})")
        
        # Store recipe inputs in state for the next step
        self.state.recipe_inputs = recipe_inputs
        logger.info(f"Préparé les entrées pour {len(recipe_inputs)} recettes")
        
        if not recipe_inputs:
            logger.warning("No valid recipe inputs could be prepared")
            return self.route_after_recipes
            
        return self.process_recipes
        
    @listen(prepare_recipe_inputs)
    def process_recipes(self):
        """
        Traite les recettes en utilisant kickoff_for_each ou en séquentiel.
        
        Cette méthode tente d'abord un traitement parallèle des recettes, puis
        revient à un traitement séquentiel en cas d'échec.
        
        Returns:
            Callable: La méthode suivante à exécuter dans le flux
        """
        recipe_inputs = self.state.recipe_inputs
        logger.info(f"Processing {len(recipe_inputs)} recipes")
        
        # Try parallel processing first
        parallel_successful = self.process_recipes_parallel()
        
        # Fall back to sequential if parallel failed
        if not parallel_successful:
            sequential_successful = self.process_recipes_sequential()
            if not sequential_successful:
                logger.error("Both parallel and sequential processing failed")
                
        return self.route_after_recipes
        
    def process_recipes_parallel(self):
        """Process recipes in parallel using kickoff_for_each."""
        recipe_inputs = self.state.recipe_inputs
        try:
            # Process recipes in parallel
            logger.info(f"Attempting parallel processing of {len(recipe_inputs)} recipes")
            recipe_expert_crew = RecipeExpertCrew().crew()
            results = recipe_expert_crew.kickoff_for_each(inputs=recipe_inputs)
            
            # Store results for tracking step
            self.state.parallel_results = results
            self.state.processing_mode = "parallel"
            logger.info(f"Completed parallel processing with {len(results)} results")
            return True
            
        except Exception as e:
            logger.error(f"Error in parallel recipe processing: {str(e)}")
            return False
    
    def process_recipes_sequential(self):
        """Process recipes sequentially as a fallback."""
        recipe_inputs = self.state.recipe_inputs
        results = []
        
        try:
            logger.info("Falling back to sequential processing")
            
            for recipe_input in recipe_inputs:
                try:
                    recipe_expert_crew = RecipeExpertCrew().crew()
                    result = recipe_expert_crew.kickoff(inputs=recipe_input)
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"Error processing recipe {recipe_input['recipe_name']}: {str(e)}")
                    results.append(None)
            
            # Store results for tracking step
            self.state.parallel_results = results
            self.state.processing_mode = "sequential"
            logger.info(f"Completed sequential processing with {len(results)} results")
            return len(results) > 0
            
        except Exception as e:
            logger.error(f"Sequential processing also failed: {str(e)}")
            # Ensure parallel_results exists even if processing failed
            self.state.parallel_results = []
            return False
            
    @router(process_recipes)
    def track_recipe_results(self):
        """
        Enregistre les résultats des recettes traitées avec succès.
        
        Cette méthode analyse les résultats du traitement (parallèle ou séquentiel)
        et met à jour l'état avec les chemins des fichiers générés pour chaque recette.
        
        Returns:
            Callable: La méthode route_after_recipes pour continuer le flux
        """
        recipe_inputs = self.state.recipe_inputs
        
        # Check if parallel_results exists in state, initialize if needed
        if not hasattr(self.state, 'parallel_results'):
            logger.warning("No parallel_results in state, initializing empty list")
            self.state.parallel_results = []
            
        results = self.state.parallel_results
        processing_mode = getattr(self.state, 'processing_mode', 'unknown')
        
        if not results:
            logger.warning("No recipe processing results to track")
            return self.route_after_recipes
            
        successful_recipes = 0
        
        # Track successful recipes
        for i, result in enumerate(results):
            if result is not None and i < len(recipe_inputs):  # Successfully processed
                recipe_input = recipe_inputs[i]
                recipe_id = recipe_input['recipe_id']
                
                # Add to tracking arrays
                self.state.recipe_ids.append(recipe_id)
                self.state.recipe_htmls.append(recipe_input['recipe_html_path'])
                self.state.recipe_yamls.append(recipe_input['recipe_yaml_path'])
                self.state.recipe_ingredients_files.append(recipe_input['recipe_ingredients_path'])
                
                logger.info(f"Successfully processed recipe: {recipe_input['recipe_name']}")
                successful_recipes += 1
            elif i < len(recipe_inputs):
                logger.warning(f"Failed to process recipe: {recipe_inputs[i]['recipe_name']}")
        
        logger.info(f"Processed {successful_recipes}/{len(recipe_inputs)} recipes via {processing_mode} mode")
        return self.route_after_recipes

    @router(track_recipe_results)
    def route_after_recipes(self):
        """
        Route le flux vers la génération de la liste de courses et du HTML.
        
        Cette méthode permet d'exécuter en parallèle les deux tâches finales
        du processus: la génération de la liste de courses et la génération
        du HTML du menu.
        
        Returns:
            Tuple: Les méthodes à exécuter en parallèle
        """
        logger.info("Routing to final output generation steps")
        return self.prepare_shopping_list, self.generate_html_output
    
    @listen(route_after_recipes)
    def prepare_shopping_list(self):
        """
        Prépare la liste de courses en utilisant ShoppingCrew.
        
        Cette méthode collecte toutes les recettes traitées et leurs ingrédients
        et utilise ShoppingCrew pour générer une liste de courses organisée.
        
        Returns:
            None: Génère les fichiers de liste de courses spécifiés
        """
        logger.info("Preparing shopping list from processed recipes")
        
        try:
            # Vérification des données nécessaires
            if not hasattr(self.state, 'recipe_ids') or not self.state.recipe_ids:
                logger.warning("No recipe IDs available for shopping list generation")
                return
                
            # Préparation des inputs pour ShoppingCrew
            inputs = {
                "recipe_list": self.state.recipe_list.model_dump() if hasattr(self.state.recipe_list, 'model_dump') else self.state.recipe_list,
                "adults": self.state.adults,
                "children": self.state.children,
                "children_age": self.state.children_age,
                "recipe_ids": self.state.recipe_ids,
                "recipe_htmls": self.state.recipe_htmls,
                "recipe_yamls": self.state.recipe_yamls,
                "recipe_ingredients_files": self.state.recipe_ingredients_files
            }
            
            # Lancement de ShoppingCrew
            logger.info(f"Starting ShoppingCrew with {len(self.state.recipe_ids)} recipes")
            shopping_crew = ShoppingCrew()
            result = shopping_crew.crew().kickoff(inputs=inputs)
            
            # Store result in state but don't return CrewOutput directly
            self.state.shopping_list_result = result
            logger.info("Shopping list generation complete")
            return True
            
        except Exception as e:
            logger.error(f"Error in shopping list generation: {str(e)}")
            return False
            
    @listen(route_after_recipes)
    def generate_html_output(self):
        """
        Génère le HTML du menu en utilisant HtmlDesignCrew.
        
        Cette méthode collecte les informations du menu et des recettes
        et utilise HtmlDesignCrew pour générer une présentation HTML complète.
        
        Returns:
            None: Génère les fichiers HTML spécifiés
        """
        logger.info("Generating HTML output for menu")
        
        # Initialize tracking arrays if they don't exist yet
        if not hasattr(self.state, 'recipe_ids'):
            self.state.recipe_ids = []
        if not hasattr(self.state, 'recipe_htmls'):
            self.state.recipe_htmls = []
        if not hasattr(self.state, 'recipe_yamls'):
            self.state.recipe_yamls = []
        if not hasattr(self.state, 'recipe_ingredients_files'):
            self.state.recipe_ingredients_files = []
        
        try:
            # Préparation des inputs pour HtmlDesignCrew
            inputs = {
                "menu_json": self.state.menu_json,
                "recipe_list": self.state.recipe_list,
                "html_output_path": "output/html_design_crew/menu.html",
                "adults": self.state.adults,
                "children": self.state.children,
                "children_age": self.state.children_age,
                "send_to": getattr(self.state, 'send_to', config.family.email)
            }
            
            # Lancement de HtmlDesignCrew
            logger.info("Starting HtmlDesignCrew to generate HTML presentation")
            html_design_crew = HtmlDesignCrew()
            result = html_design_crew.crew().kickoff(inputs=inputs)
            
            # Store result in state but don't return CrewOutput directly
            self.state.html_result = result
            logger.info("HTML generation complete")
            return True
            
        except Exception as e:
            logger.error(f"Error in HTML generation: {str(e)}")
            return False

def kickoff():
    menu_flow = MenuFlow()
    menu_flow.kickoff()


def plot():
    menu_flow = MenuFlow()
    menu_flow.plot()


if __name__ == "__main__":
    kickoff()
