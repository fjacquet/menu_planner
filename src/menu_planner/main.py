#!/usr/bin/env python
from random import randint
import json


from crewai.flow import Flow, and_, listen, router, start

from menu_planner.schemas import RecipeList, MenuJson, MenuState

from menu_planner.crews.poem_crew.poem_crew import PoemCrew
from menu_planner.crews.menu_designer_crew.menu_designer_crew import MenuDesignerCrew
from menu_planner.crews.html_design_crew.html_design_crew import HtmlDesignCrew

class PoemFlow(Flow[MenuState]):

    @start()
    def generate_sentence_count(self):
        print("Generating sentence count")
        self.state.sentence_count = randint(1, 5)

    @listen(generate_sentence_count)
    def generate_poem(self):
        print("Generating poem")
        inputs = {"sentence_count": self.state.sentence_count}
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
            "recipe_list": self.state.recipe_list,
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
        # inputs = {
        #     "adults": self.state.adults,
        #     "children": self.state.children,
        #     "children_age": self.state.children_age,
        #     "menu_json": self.state.menu_json,
        #     "recipe_list": self.state.recipe_list, 
        #     "poem": self.state.poem,
        # }
        HtmlDesignCrew().crew().kickoff(inputs=inputs)

def kickoff():
    poem_flow = PoemFlow()
    poem_flow.kickoff()


def plot():
    poem_flow = PoemFlow()
    poem_flow.plot()


if __name__ == "__main__":
    kickoff()
