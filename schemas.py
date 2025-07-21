from pydantic import BaseModel, Field
from typing import List, Optional

class UserProfile(BaseModel):
    age: int
    sex: str
    height_cm: float
    weight_kg: float
    activity_level: str
    health_goals: List[str]
    dietary_restrictions: Optional[List[str]] = []

class FoodItem(BaseModel):
    name: str
    nutrients: dict

class MealPlan(BaseModel):
    id: str
    version: int
    week_number: int
    meals: List[List[FoodItem]]
    notes: Optional[str]

class NutritionSummary(BaseModel):
    total_intake: dict
    gaps: dict

class RecipeSuggestion(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str
    nutrient_profile: dict

class ConfirmationFlags(BaseModel):
    profile_confirmed: bool = False
    diet_confirmed: bool = False
    recipe_confirmed: bool = False
    grocery_confirmed: bool = False

class RouterIntent(BaseModel):
    intent: str
    agent: str
    target_week: Optional[int] = None
    modification: Optional[str] = None

class TriggerSuggestion(BaseModel):
    agent: str
    reason: str
    suggested: bool = True
