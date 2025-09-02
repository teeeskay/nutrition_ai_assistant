from pydantic import BaseModel
from typing import List, Optional, Literal

class UserProfile(BaseModel):
    age_years: int # no. of years old
    age_months: Optional[int] = None # no. of months if user provides, irregardless of no. of years i.e. this is NOT a conversion of age_years

    gender: Literal["female", "male"] # other genders later, as data is primarily categorised by these 2 genders
    height_cm: float
    weight_kg: float
    physical_activity_level_description: str
    physical_activity_level_PAL: float # PAL multiplier
    
    # mention in UI that health statuses such as pregnancy and lactation are handled later
    #is_pregnant: Optional[bool] = False # while there's data available, we'll handle logic for pregnancy and lactation later
    #pregnancy_stage: Optional[Literal["1st_trimester", "2nd_trimester", "3rd_trimester"]] = None
    #is_lactating: Optional[bool] = False
    #lactation_stage: Optional[Literal["0-6_months", ">6_months"]] = None
    
    lean_body_mass: Optional[float] = None # for Cunningham equation
    
    #health_goals: List[str]
    #dietary_restrictions: Optional[List[str]] = []

    @property
    def total_age_years(self) -> float: # sum of age_years and age_months
        months = 0 if self.age_months is None else self.age_months
        return self.age_years + months / 12


class UserProfilePartial(BaseModel):
    # All optional: used only for incremental extraction/merging
    age_years: Optional[int] = None
    age_months: Optional[int] = None
    gender: Optional[Literal["female", "male"]] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    physical_activity_level_description: Optional[str] = None
    physical_activity_level_PAL: Optional[float] = None


class NutrientNeed(BaseModel):
    nutrient: str
    unit: str
    drv_type: Literal["PRI", "AI", "AR", "RI", "UL"]
    # PRI = Population Reference Intake (PRI = AR + 2*SD), AI = Adequate Intake, AR = Adequate Requirement, UL = Tolerable Upper Intake Level
    # value representation
    value_type: Literal["exact", "range", "alap", "zero"]
    numeric_value: Optional[float] = None
    range_lower: Optional[float] = None
    range_upper: Optional[float] = None
    original_value: Optional[str] = None
    notes: Optional[str] = None
    phytate_level: Optional[float] = None  # for zinc rows with zinc_phytate_mgpd
    # derived representation (computed per user)
    derived_value_type: Optional[Literal["exact", "range"]] = None
    derived_numeric_value: Optional[float] = None
    derived_range_lower: Optional[float] = None
    derived_range_upper: Optional[float] = None
    derived_unit: Optional[str] = None
    derived_notes: Optional[str] = None



### below was scaffolded and requires editing

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
