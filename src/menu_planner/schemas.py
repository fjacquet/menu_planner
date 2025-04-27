from pydantic import BaseModel
from typing import Optional

class RecipeList(BaseModel):
    recipes: list[str] = []

class Meal(BaseModel):
    title: str
    description: str
    calories: int

class DayMenu(BaseModel):
    lunch: Meal
    dinner: Meal

class WeeklyMenu(BaseModel):
    monday: DayMenu
    tuesday: DayMenu
    wednesday: DayMenu
    thursday: DayMenu
    friday: DayMenu
    saturday: DayMenu
    sunday: DayMenu

class MenuJson(BaseModel):
    weekly_menu: WeeklyMenu

class Poem(BaseModel):
    sentence_count: int = 1
    poem: str = ""

class MenuState(BaseModel):
    menu_json: Optional[MenuJson] = None
    menu_html: str = ""
    adults: int = 2
    children: int = 1
    children_age: int = 10
    recipe_list: Optional[RecipeList] = None
    sentence_count: int = 1
    poem: str = ""
    
    # Recipe tracking lists
    recipe_ids: list[str] = []
    recipe_htmls: list[str] = []
    recipe_yamls: list[str] = []
    recipe_ingredients_files: list[str] = []