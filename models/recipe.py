from pydantic import BaseModel
from typing import Optional, Union


class RecipeInstruction(BaseModel):
    instruction: str
    ingredients: list[int]
    equipment: list[Union[str, int]]
    duration: Optional[int]


class RecipeIngredient(BaseModel):
    id: int
    name: str
    aisle: Optional[str] = None
    image: Optional[str] = None
    amount: float
    unit_short: str
    unit_long: str
    original_string: str
    meta_information: list[str]


class Recipe(BaseModel):
    id: int
    spoonacular_id: int
    recipe_name: str
    image_link: str
    price: float
    cuisine_type: str
    vegetarian: bool
    vegan: bool
    prep_cook_time: int
    servings: int
    instructions: list[RecipeInstruction]
    ingredients: list[RecipeIngredient]


class WeeklyMealPlan(BaseModel):
    id: int
    meal_plan_name: str
    meal_plan_type: str
    cuisine_type: str
    vegetarian: bool
    vegan: bool
    recipes: list[Recipe]
