#from langgraph.graph import MessageGraph, StateGraph
#from langgraph.graph.message import add_messages
#from langgraph.graph import compile_graph
#from langgraph.utils import load_graph
from dotenv import load_dotenv; load_dotenv()
import os
from langgraph.types import Command
from langchain_core.messages import HumanMessage
from nutrition_graph.build_graph import app

def run_graph():
    #graph = load_graph("langgraph/planner.graph.yaml")
    #app = compile_graph(graph)
    #app = graph.compile()

    first = input("Hi! tell me a bit about yourself:\n>> ")
    state = {
        "messages": [HumanMessage(content=first)], 
        "user_profile": {},
        "profile_validation_status": "incomplete",
        "missing_fields": [],
        "error": None
    }
    #state = add_messages({}, "user_input", {"user_input": user_input})
    #state["user_profile"] = {}

    cfg = {"configurable": {"thread_id": "cli"}}

    first_run = True
    while True:
        interrupted = False
        # Only pass the full state on the first run; afterwards rely on checkpointer + resume
        stream_input = state if first_run else None
        for event in app.stream(stream_input, cfg, stream_mode="updates"):
            if "__interrupt__" in event:
                prompt = event["__interrupt__"][0].value
                print("\n" + str(prompt))
                ans = input(">> ")
                # Resume the graph with the user's answer; do not reset or resend state
                for _ in app.stream(Command(resume=ans), cfg, stream_mode="updates"):
                    pass
                interrupted = True
                break

            if "nutrient_needs" in event or ("energy_kcal" in event and event["energy_kcal"] is not None):
                final = app.get_state(cfg).values
                print("\nEstimated energy:", final.get("energy_kcal"), "kcal/day")
                if final.get("warning"):
                    print("Note:", final.get("warning"))
                for n in (final.get("nutrients") or []):
                    if n['value_type'] == 'exact':
                        print(f"{n['nutrient']}: {n['numeric_value']} {n['unit']} ({n['drv_type']})")
                    elif n['value_type'] == 'range':
                        print(f"{n['nutrient']}: {n['range_lower']}-{n['range_upper']} {n['unit']} ({n['drv_type']})")
                    elif n['value_type'] == 'alap':
                        print(f"{n['nutrient']}: ALAP {n['unit']} ({n['drv_type']})")
                    elif n['value_type'] == 'zero':
                        print(f"{n['nutrient']}: 0 {n['unit']} ({n['drv_type']})")

                    # Derived values
                    if n.get('derived_value_type') == 'exact':
                        print(f"  ≈ {n['derived_numeric_value']} {n['derived_unit']} ({n.get('derived_notes','derived')})")
                    elif n.get('derived_value_type') == 'range':
                        print(f"  ≈ {n['derived_range_lower']}-{n['derived_range_upper']} {n['derived_unit']} ({n.get('derived_notes','derived')})")
                    
                    if n.get('phytate_level'):
                        print(f"  (Phytate level: {n['phytate_level']} mg/d)")
                    if n.get('notes'):
                        print(f"  Note: {n['notes']}")
                return
            
        # After first iteration, don't resend the full state again
        first_run = False
        if not interrupted:
            # Ensure we print final results even if no single event carried the key
            final = app.get_state(cfg).values
            if final.get("energy_kcal") is not None:
                print("\nEstimated energy:", final.get("energy_kcal"), "kcal/day")
                if final.get("warning"):
                    print("Note:", final.get("warning"))
                for n in (final.get("nutrients") or []):
                    if n['value_type'] == 'exact':
                        print(f"{n['nutrient']}: {n['numeric_value']} {n['unit']} ({n['drv_type']})")
                    elif n['value_type'] == 'range':
                        print(f"{n['nutrient']}: {n['range_lower']}-{n['range_upper']} {n['unit']} ({n['drv_type']})")
                    elif n['value_type'] == 'alap':
                        print(f"{n['nutrient']}: ALAP {n['unit']} ({n['drv_type']})")
                    elif n['value_type'] == 'zero':
                        print(f"{n['nutrient']}: 0 {n['unit']} ({n['drv_type']})")

                    # Derived values
                    if n.get('derived_value_type') == 'exact':
                        print(f"  ≈ {n['derived_numeric_value']} {n['derived_unit']} ({n.get('derived_notes','derived')})")
                    elif n.get('derived_value_type') == 'range':
                        print(f"  ≈ {n['derived_range_lower']}-{n['derived_range_upper']} {n['derived_unit']} ({n.get('derived_notes','derived')})")
                    
                    if n.get('phytate_level'):
                        print(f"  (Phytate level: {n['phytate_level']} mg/d)")
                    if n.get('notes'):
                        print(f"  Note: {n['notes']}")
                return
            break

    """while True:
        result = app.invoke(state)
        state.update(result)

        if result.get("error"):
            print("❌ LLM failed to extract profile:\n", result["error"])
            break

        if result.get("nutrients") is not None:
            print("\n Here's your nutrient needs:")
            print(f"Estimated energy: {result['energy_kcal']} kcal/day\n")
            for n in result["nutrients"]:
                print(f"{n['nutrient']}: {n['value']} {n['unit']} ({n['drv_type']})")
            break

        if result.get("followup_prompt"):
            print("\n" + result["followup_prompt"])
            user_input = input(">> ")
            state["messages"].append({"role": "user", "content": user_input})
            #state = add_messages(state, "user_input", {"user_input": user_input})
        
        else:
            print("Unexpected result:", result)
            break
    """

if __name__ == "__main__":
    run_graph()