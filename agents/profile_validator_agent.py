from typing import Dict

REQUIRED_FIELDS = [
    "age_years", "gender",
    "height_cm", "weight_kg",
    "physical_activity_level_description" #, "physical_activity_level_PAL"
]

#def profile_validator_agent(state: Dict) -> str:
def validate_profile_node(state: dict) -> dict:
    profile = state.get("user_profile", {}) or {}
    missing = [f for f in REQUIRED_FIELDS if not profile.get(f)]
    status = "complete" if not missing else "incomplete"
    #return result, {**state, "profile_validation_status": result}
    #return result, statede
    return {
        "profile_validation_status": status,
        "missing_fields": missing
    }

def route_after_validation(state: dict) -> str:
    return "complete" if state.get("profile_validation_status") == "complete" else "incomplete"