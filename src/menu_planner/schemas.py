from pydantic import BaseModel, AnyHttpUrl
from typing import Optional, List
import os

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

class RecipeIngredient(BaseModel):
    name: str
    quantity: float
    unit: str

class RecipeOutput(BaseModel):
    recipe_html: str
    ingredients: list[RecipeIngredient]

class MenuState(BaseModel):
    menu_json: Optional[MenuJson] = None
    menu_html: str = ""
    adults: int = int(os.getenv("ADULTS", "2"))
    children: int = int(os.getenv("CHILDREN", "1"))
    children_age: int = int(os.getenv("CHILDREN_AGE", "10"))
    recipe_list: Optional[RecipeList] = None
    sentence_count: int = 1
    poem: str = ""
    
    # Recipe tracking lists
    recipe_ids: list[str] = []
    recipe_htmls: list[str] = []
    recipe_yamls: list[str] = []
    recipe_ingredients_files: list[str] = []

class PaprikaRecipe(BaseModel):
    name: str
    servings: str
    source: Optional[str]
    source_url: Optional[AnyHttpUrl]
    prep_time: str
    cook_time: Optional[str]
    on_favorites: Optional[str]
    categories: List[str]
    nutritional_info: Optional[str]
    difficulty: str
    rating: Optional[int]
    notes: Optional[str]
    photo: Optional[str]
    ingredients: str
    directions: str