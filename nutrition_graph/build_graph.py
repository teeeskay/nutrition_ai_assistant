from typing_extensions import TypedDict, Annotated
from typing import List, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from agents.profile_extractor_agent import profile_extractor_agent
from agents.profile_validator_agent import validate_profile_node, route_after_validation #profile_validator_agent
from agents.prompt_builder_agent import prompt_builder_agent
from agents.nutrient_needs_agent import nutrient_needs_node #nutrient_needs_agent

class GraphState(TypedDict):
    messages: Annotated[list, add_messages]
    user_profile: dict
    profile_validation_status: str
    missing_fields: List[str]
    followup_prompt: Optional[str]
    nutrients: list
    energy_kcal: float
    error: Optional[str]

graph = StateGraph(state_schema=GraphState)

graph.add_node("extract_profile", profile_extractor_agent)
graph.add_node("validate_profile", validate_profile_node) #profile_validator_agent)
graph.add_node("prompt_user", prompt_builder_agent)
graph.add_node("nutrient_needs", nutrient_needs_node)

graph.set_entry_point("extract_profile")
graph.add_edge("extract_profile", "validate_profile")
graph.add_conditional_edges("validate_profile",
                            route_after_validation,
                            #validate_profile_node,
                            #profile_validator_agent,
                            {"complete": "nutrient_needs", "incomplete": "prompt_user"})
graph.add_edge("prompt_user", "extract_profile")
#graph.add_edge("prompt_user")
graph.add_edge("nutrient_needs", END)

memory = InMemorySaver()
app = graph.compile(checkpointer=memory)