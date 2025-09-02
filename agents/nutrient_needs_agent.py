# This agent figures out nutrient targets for a user based on their profile
#
# Demographics: Age, Gender, Height, Weight
#
# Do this later, and mention this as a disclaimer that we do not factor in conditions, allergies or medical-related dietary needs.
# Health Status: Known Dietary Needs or Restrictions based on Conditions (but no we do not factor in conditions and their implications,
# we only factor in known restrictions and allergies), Allergies
#
# Activity Level: Physical activity level, Sedentary vs Active
# - How many days per week do you exercise?
# - On average, how long is each session?
# - What type of activity do you usually do? (e.g., walking, running, strength training, sports)
# - How would you rate your activity intensity? (light, moderate, vigorous)
# - Do you have a physically active job or lifestyle? (e.g. on your feet all day, walking 10k+ steps)
#
# Atwater system factors (metabolizable energy):
# - Protein: 4 kcal/g
# - Carbohydrate: 4 kcal/g
# - Fat: 9 kcal/g
# - Alcohol: 7 kcal/g

import pandas as pd
import re
from shared.schemas import UserProfile, NutrientNeed

drv_male = pd.read_csv("data/drv_male.csv") # need to combine tables and add data
#drv_female = pd.read_csv("data/drv_female.csv") # need to combine tables and add data
drv_female = pd.read_csv("data/drv_female_fake_data.csv")

#def get_nutrient_needs(profile: UserProfile) -> list[NutrientNeed]:

def get_nutrient_needs(profile: UserProfile) -> tuple[list[NutrientNeed], str | None]:
    table = drv_male if profile.gender == "male" else drv_female
    #is_preg = profile.is_pregnant or False
    #is_lact = profile.is_lactating or False

    #if profile.gender == "female":
    #    if is_preg:
    # ...

    #user_age = profile.total_age_years

    #margin = 1e-6
    #matched_rows = table[
    #    (abs(table["total_age_years"] - user_age) < margin)
    #]

    # Age matching per data schema:
    # - age_years 1..25 (ignore months)
    # - age_years == 0 uses age_months in 7..11
    age_years = int(profile.age_years)
    age_months = 0 if profile.age_months is None else int(profile.age_months)

    warning_message: str | None = None
    if {"age_years", "age_months"}.issubset(table.columns):
        if age_years == 0:
            # Clamp months to 7..11
            if age_months <= 6:
                warning_message = (
                    "Data available only from 7 months or older; using 0 years 7 months values."
                )
                m = 7
            else:
                m = max(7, min(11, age_months))
            matched_rows = table[(table["age_years"] == 0) & (table["age_months"] == m)]
        else:
            # For ages 25 or older, use values for 25 years
            clamped_age = 25 if age_years >= 25 else age_years
            matched_rows = table[(table["age_years"] == clamped_age)]
    else:
        # Fallbacks for alternate schemas
        user_age = profile.total_age_years
        margin = 1e-6
        if "total_age_years" in table.columns:
            matched_rows = table[(table["total_age_years"] - user_age).abs() < margin]
        elif {"age_min", "age_max"}.issubset(table.columns):
            matched_rows = table[(table["age_min"] <= user_age) & (user_age <= table["age_max"])]
        elif {"age_min_years", "age_max_years"}.issubset(table.columns):
            matched_rows = table[(table["age_min_years"] <= user_age) & (user_age <= table["age_max_years"])]
        else:
            print("Warning: DRV table missing age columns; nutrients will be empty. Columns:", list(table.columns))
            matched_rows = table.iloc[0:0]

    def _parse_value(raw: object) -> dict | None:
        # Returns a dict suitable for NutrientNeed value fields, or None to skip
        if raw is None or (isinstance(raw, float) and pd.isna(raw)):
            return {"value_type": "zero", "numeric_value": 0.0}
        if isinstance(raw, (int, float)):
            return {"value_type": "exact", "numeric_value": float(raw)}
        if isinstance(raw, str):
            s = raw.strip()
            if not s:
                return {"value_type": "zero", "numeric_value": 0.0}
            s_norm = s.replace("–", "-")
            if s_norm.upper() == "ALAP":
                return {"value_type": "alap", "original_value": s}
            m = re.match(r"^(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$", s_norm)
            if m:
                lo, hi = float(m.group(1)), float(m.group(2))
                return {
                    "value_type": "range",
                    "range_lower": lo,
                    "range_upper": hi,
                    "original_value": s,
                }
            try:
                return {"value_type": "exact", "numeric_value": float(s)}
            except Exception:
                return None
        return None

    # Helpers to compute derived grams from E% or g/kg
    def _derive_from_e_percent(e_percent: float, energy_kcal: float, macro: str) -> float:
        if macro == "fat":
            return round((e_percent / 100.0) * energy_kcal / 9.0, 1)
        if macro == "carb":
            return round((e_percent / 100.0) * energy_kcal / 4.0, 1)
        if macro == "protein":
            return round((e_percent / 100.0) * energy_kcal / 4.0, 1)
        return 0.0

    nutrient_needs: list[NutrientNeed] = []
    for _, row in matched_rows.iterrows():
        parsed = _parse_value(row.get("value"))
        if parsed is None:
            continue

        # Now validate unit: allow missing for ALAP, require for others
        raw_unit = row.get("unit")
        if parsed.get("value_type") != "alap":
            if pd.isna(raw_unit) or not isinstance(raw_unit, str):
                continue
            unit_str = raw_unit
        else:
            # Keep unit empty if missing for ALAP
            unit_str = "" if (pd.isna(raw_unit) or not isinstance(raw_unit, str)) else str(raw_unit)

        # Handle phytate level for zinc (age 18+)
        phytate_level = None
        notes = None
        if "notes" in row and isinstance(row["notes"], str) and row["notes"].strip():
            notes = row["notes"].strip()

        if "zinc_phytate_mgpd" in row and not pd.isna(row["zinc_phytate_mgpd"]):
            phytate_level = float(row["zinc_phytate_mgpd"])
            phytate_note = f"Phytate level: {phytate_level} mg/d"
            notes = f"{notes + ' | ' if notes else ''}{phytate_note}"

        nn = NutrientNeed(
            nutrient=row["nutrient"],
            unit=unit_str,
            drv_type=row["drv_type"],
            notes=notes,
            phytate_level=phytate_level,
            **parsed,
        )

        # Derived targets per user
        energy_kcal = estimate_energy_needs(profile)
        if nn.value_type == "exact":
            # protein in g/kg bw per day
            if isinstance(unit_str, str) and unit_str.lower().startswith("g/kg"):
                nn.derived_value_type = "exact"
                nn.derived_numeric_value = round(float(nn.numeric_value) * profile.weight_kg, 1)
                nn.derived_unit = "g/d"
                nn.derived_notes = "Derived from g/kg bw per day"
            # E% for fat/carb/protein
            elif unit_str == "E%":
                macro = "fat" if "fat" in row["nutrient"].lower() else ("carb" if "carb" in row["nutrient"].lower() else "protein")
                grams = _derive_from_e_percent(float(nn.numeric_value), energy_kcal, macro)
                nn.derived_value_type = "exact"
                nn.derived_numeric_value = grams
                nn.derived_unit = "g/d"
                nn.derived_notes = "Derived using Atwater factors"
        elif nn.value_type == "range" and unit_str == "E%":
            macro = "fat" if "fat" in row["nutrient"].lower() else ("carb" if "carb" in row["nutrient"].lower() else "protein")
            low = _derive_from_e_percent(float(nn.range_lower), energy_kcal, macro)
            high = _derive_from_e_percent(float(nn.range_upper), energy_kcal, macro)
            nn.derived_value_type = "range"
            nn.derived_range_lower = low
            nn.derived_range_upper = high
            nn.derived_unit = "g/d"
            nn.derived_notes = "Derived using Atwater factors"

        nutrient_needs.append(nn)

    return nutrient_needs, warning_message

def estimate_energy_needs(profile: UserProfile) -> float:
    # Basal Metabolic Rate (BMR) estimated using the Mifflin-St Jeor equation 
    # since EFSA's AR values for energy (which uses the Schofield equation) are likely less accurate
    if profile.gender == "male":
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.total_age_years + 5
    elif profile.gender == "female":
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.total_age_years - 161
    
    # Return total energy needs by multiplying user's physical activity level, 
    # ranging from a 1.2 to 2.5+ multiplier categorised based on user's description
    return round(bmr * profile.physical_activity_level_PAL, 1)

def nutrient_needs_agent(profile: UserProfile) -> dict:
    nutrient_needs, warning_message = get_nutrient_needs(profile)
    energy_kcal_needs = estimate_energy_needs(profile)
    return {
        "energy_kcal": energy_kcal_needs,
        "nutrients": [n.model_dump() for n in nutrient_needs],
        "warning": warning_message,
    }

def nutrient_needs_node(state: dict) -> dict:
    profile = UserProfile(**(state.get("user_profile") or {}))
    out = nutrient_needs_agent(profile)
    return out