from pydantic import BaseModel
from typing import Optional



class GenerateMealPlanRequest(BaseModel):
    user_id: int 
    vegan: bool
    vegetarian: bool
    price_per_meal: float
    
class MealPlanResponse(BaseModel):
    meal_plan_id: int
    recipes: list[int]
    
