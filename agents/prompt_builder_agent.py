from typing import Dict
from langgraph.types import interrupt
from langchain_core.messages import HumanMessage

REQUIRED_FIELDS = [
    "age_years", "gender",
    "height_cm", "weight_kg",
    "physical_activity_level_description"
]

def prompt_builder_agent(state: dict) -> dict:
    profile = state.get("user_profile", {}) or {}
    missing = state.get("missing_fields") or [f for f in REQUIRED_FIELDS if not profile.get(f)]
    
    questions = {
        "age_years": "How old are you (in years)?",
        "age_months": "Any extra months (eg. 6 months)?",
        "gender": "What is your gender (male or female)? Sorry we currently only support these 2.",
        "height_cm": "What is your height in cm?",
        "weight_kg": "What is your weight in kg?",
        "physical_activity_level_description": "How active are you? eg. sedentary, moderately active"
    }
    lines = [questions[f] for f in missing if f in questions]
    prompt = "I still need a few more details:\n" + "\n".join(lines) if lines else "Could you add any missing details?"

    user_reply = interrupt(prompt)

    return {"messages": [HumanMessage(content=user_reply)]}
    #return {"followup_prompt": msg}


# Activity Level: Physical activity level, Sedentary vs Active
# - How many days per week do you exercise?
# - On average, how long is each session?
# - What type of activity do you usually do? (e.g., walking, running, strength training, sports)
# - How would you rate your activity intensity? (light, moderate, vigorous)
# - Do you have a physically active job or lifestyle? (e.g. on your feet all day, walking 10k+ steps)