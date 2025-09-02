#from langchain_community.chat_models import ChatOllama
#from langchain_ollama import ChatOllama

from langchain_openai import ChatOpenAI

from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

from shared.schemas import UserProfile, UserProfilePartial
from shared.pal_mapper import map_activity_description_to_pal
from typing import Dict
import re

import os

#def profile_extractor_agent(state: dict, input: dict) -> dict:
def profile_extractor_agent(state: dict) -> dict:    
    #user_input = input["user_input"]

    messages = state.get("messages", [])
    user_input = messages[-1].content if messages else state.get("user_input", "")
    #user_input = state.get("user_input", "")
    previous_profile = state.get("user_profile", {}) or {}

    #parser = PydanticOutputParser(pydantic_object=UserProfile)
    # Parse incrementally into a partial profile
    parser = PydanticOutputParser(pydantic_object=UserProfilePartial)

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a strict JSON API for extracting nutrition profiles.\n"
            "Rules:\n"
            "- Output ONLY valid JSON, no extra text.\n"
            "- Use this schema (all fields optional in your output):\n"
            f"{parser.get_format_instructions().replace('{', '{{').replace('}', '}}')}\n"
            "- Current known profile is provided; DO NOT overwrite known fields unless the user provides a clear update.\n"
            "- Only include fields you can reliably extract from the user's latest message.\n"
            #"You are a strict JSON API. Your job is to extract structured nutrition profile data from user input.\n"
            #"Do NOT reply with greetings, explanations, or text.\n"
            #"Always respond ONLY with valid JSON following this schema:\n"
            #f"{parser.get_format_instructions().replace('{', '{{').replace('}', '}}')}"
        )),
        ("system", "Current known profile: {previous_profile}"),
        ("user", "{user_input}")
    ])

    #llm = ChatOllama(model="mistral", temperature=0)
    #llm = ChatOllama(model="gemma3n:e4b", temperature=0)
    #llm = ChatOllama(model="gemma3:1b", temperature=0)
    llm_provider = os.getenv("LLM_PROVIDER")
    llm_model = os.getenv("LLM_MODEL")
    
    llm = ChatOpenAI(
        model=llm_model, 
        temperature=0,
        openai_api_key=os.getenv("GROQ_API_KEY"),
        openai_api_base="https://api.groq.com/openai/v1"
        )

    chain = prompt | llm | parser

    try:
        output = chain.invoke({"user_input": user_input, "previous_profile": previous_profile})
        print("[LLM RAW OUTPUT]", output)
        new_profile: UserProfilePartial = output
    except Exception as e:
        # Fallback: try to regex-parse common short replies like "36yo male 174cm 86kg"
        text = user_input.lower()
        fallback: Dict = {}
        try:
            if m := re.search(r"(\d+)\s*(?:yo|yrs|years)", text):
                fallback["age_years"] = int(m.group(1))
            if m := re.search(r"\b(male|female)\b", text):
                fallback["gender"] = m.group(1)
            if m := re.search(r"(\d+(?:\.\d+)?)\s*cm", text):
                fallback["height_cm"] = float(m.group(1))
            if m := re.search(r"(\d+(?:\.\d+)?)\s*kg", text):
                fallback["weight_kg"] = float(m.group(1))
            # PAL words
            if any(w in text for w in ["sedentary", "light", "moderate", "very active", "vigorous"]):
                fallback["physical_activity_level_description"] = text
        except Exception:
            pass
        if not fallback:
            return {**state, "error": f"Failed to parse profile: {e}"}
        new_profile = UserProfilePartial(**fallback)
    
    merged = previous_profile.copy()
    for k, v in new_profile.model_dump().items():
        if v is not None:
            merged[k] = v

    if merged.get("physical_activity_level_PAL") is None and merged.get("physical_activity_level_description"):
        merged["physical_activity_level_PAL"] = map_activity_description_to_pal(merged["physical_activity_level_description"])

    #return {**state,"user_profile": merged}
    print("[MERGED PROFILE]", merged)
    return {"user_profile": merged, "error": None}


# def profile_extractor_agent(user_input: str) -> UserProfile:
    