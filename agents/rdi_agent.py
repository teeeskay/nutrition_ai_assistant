from shared.schemas import UserProfile, NutritionSummary

def run(input: dict) -> dict:
    profile = UserProfile(**input["profile"])
    # Dummy RDI calculation
    rdi_targets = {
        "calories": 2000,
        "protein": 50,
        "vitamin_d": 15,
        "iron": 18
    }
    return {"rdi_targets": rdi_targets}
