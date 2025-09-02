
# needs agent to answer relevant questions for user to input answers that are then categorised as one of the following 
# or clarified if user's input isn't relevant

def map_activity_description_to_pal(desc: str) -> float:
    desc = desc.lower()
    if "sedentary" in desc:
        return 1.2
    elif "light" in desc:
        return 1.375
    elif "moderate" in desc:
        return 1.55
    elif "very active" in desc or "vigorous" in desc:
        return 1.725
    elif "extra active" in desc:
        return 1.9
    return 1.55