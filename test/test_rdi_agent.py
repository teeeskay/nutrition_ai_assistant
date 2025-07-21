from agents.rdi_agent import run

def test_rdi_output_format():
    input_data = {"profile": {
        "age": 30,
        "sex": "male",
        "height_cm": 175,
        "weight_kg": 70,
        "activity_level": "moderate",
        "health_goals": ["maintain muscle"],
        "dietary_restrictions": []
    }}
    result = run(input_data)
    assert "rdi_targets" in result
    assert isinstance(result["rdi_targets"], dict)
