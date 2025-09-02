from shared.schemas import UserProfile
from agents.nutrient_needs_agent import nutrient_needs_agent

def test_nutrient_agent_for_male():
    profile = UserProfile(
        age_years=36,
        age_months=0,
        gender="male",
        weight_kg=85,
        height_cm=174,
        physical_activity_level_PAL=1.6
    )
    result = nutrient_needs_agent(profile)
    
    assert "energy_kcal" in result
    assert isinstance(result["energy_kcal"], float)

    assert isinstance(result, dict)
    
    assert "nutrients" in result
    assert isinstance(result["nutrients"], list)
    assert all(isinstance(n, dict) for n in result["nutrients"])

    assert any(n["nutrient"] == "Vitamin C" for n in result["nutrients"])
