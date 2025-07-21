def route_intents(state):
    msg = state.get("latest_message", "").lower()
    if "recipe" in msg:
        return "recipe_agent"
    elif "diet" in msg:
        return "profile_agent"
    elif "grocery" in msg:
        return "grocery_agent"
    return "profile_agent"
