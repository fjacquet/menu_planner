#!/usr/bin/env python
from random import randint
import json

from crewai.flow import Flow, and_, listen, router, start

from menu_planner.schemas import RecipeList, MenuJson, MenuState

from menu_planner.crews.poem_crew.poem_crew import PoemCrew
from menu_planner.crews.menu_designer_crew.menu_designer_crew import MenuDesignerCrew
from menu_planner.crews.html_design_crew.html_design_crew import HtmlDesignCrew
from menu_planner.crews.recipe_expert_crew.recipe_expert_crew import RecipeExpertCrew
from menu_planner.crews.shopping_crew.shopping_crew import ShoppingCrew

class PoemFlow(Flow[MenuState]):

    @start()
    def generate_sentence_count(self):
        print("Generating sentence count")
        self.state.sentence_count = randint(1, 5)

    @listen(generate_sentence_count)
    def generate_poem(self):
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
        print("Démarrage de la génération du menu hebdomadaire")
        inputs = {
            "adults": self.state.adults,
            "children": self.state.children,
            "children_age": self.state.children_age,
            "menu_json": self.state.menu_json,
            "menu_html": self.state.menu_html,
            "recipe_list": self.state.recipe_list,
            "send_to": self.state.send_to,

        }
        MenuDesignerCrew().crew().kickoff(inputs=inputs)

        with open("output/menu_designer_crew/liste_recettes.json", "r") as f:
            self.state.recipe_list = RecipeList(**json.load(f))

        with open("output/menu_designer_crew/menu.json", "r") as f:
            self.state.menu_json = MenuJson(**json.load(f))

    @router(and_("generate_menu", "generate_poem"))
    def check_state(self):  

        recipes = self.state.recipe_list
        print("Recipes", recipes)

        menu = self.state.menu_json
        print("Menu", menu)

    @listen(check_state)
    def insert_poem(self):
        inputs = {
            "adults": self.state.adults,
            "children": self.state.children,
            "children_age": self.state.children_age,
            "menu_json": self.state.menu_json.model_dump() if self.state.menu_json else None,
            "recipe_list": self.state.recipe_list.model_dump() if self.state.recipe_list else None,
            "poem": self.state.poem,
            }   
        HtmlDesignCrew().crew().kickoff(inputs=inputs)

    @listen(insert_poem)
    def prepare_recipes(self):
        recipe_list = self.state.recipe_list
        
        # Lists to track generated files
        recipe_ids = []
        recipe_htmls = []
        recipe_yamls = []
        recipe_ingredients_files = []
        
        if recipe_list:
            for recipe in recipe_list.recipes:
                print(recipe)
                recipe_id = recipe.lower().replace(" ", "_")
                recipe_html = f"output/recipe_expert_crew/{recipe_id}.html"
                recipe_yaml = f"output/recipe_expert_crew/{recipe_id}.yaml"
                recipe_ingredients = f"output/recipe_expert_crew/{recipe_id}_ingredients.json"
                
                # Process each recipe
                RecipeExpertCrew().crew().kickoff(
                    inputs={
                        "recipe": recipe,
                        "recipe_id": recipe_id,
                        "recipe_html_path": recipe_html,
                        "recipe_yaml_path": recipe_yaml,
                        "recipe_ingredients_path": recipe_ingredients,
                    }
                )
                # Add to tracking lists
                recipe_ids.append(recipe_id)
                recipe_htmls.append(recipe_html)
                recipe_yamls.append(recipe_yaml)
                recipe_ingredients_files.append(recipe_ingredients)
        else:
            print("No recipes found.")
        
        # Save tracked lists to state for use in shopping_list
        self.state.recipe_ids = recipe_ids
        self.state.recipe_htmls = recipe_htmls
        self.state.recipe_yamls = recipe_yamls
        self.state.recipe_ingredients_files = recipe_ingredients_files

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
    poem_flow = PoemFlow()
    poem_flow.kickoff()


def plot():
    poem_flow = PoemFlow()
    poem_flow.plot()


if __name__ == "__main__":
    kickoff()
