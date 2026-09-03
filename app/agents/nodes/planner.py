from app.agents.state import AgentState
from app.agents.schema import PlannerDecision
import logfire
from app.gateway import get_langchain_llm



llm = get_langchain_llm(feature="planner")


structured_llm = llm.with_structured_output(PlannerDecision)

def planner_node(state: AgentState):
    """
    The Planner determines if a search is needed based on the ENTIRE conversation.
    """
    # Get the conversation history (excluding the latest message)
    history = ""
    for msg in state["messages"][:-1]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history += f"{role}: {msg['content']}\n"
    
    user_message = state["messages"][-1]["content"] if state["messages"] else ""
    
    prompt = f"""
    You are an intelligent Assistant Planner. 
    Analyze the conversation history and the latest user message.
    
    CONVERSATION HISTORY:
    {history}
    
    LATEST MESSAGE:
    "{user_message}"
    
    Task:
    1. If the latest message is a greeting or a question answerable ONLY from
       the conversation history above (e.g. "what is my name"), set intent to
       "conversational".
    2. If it is a technical question about Kubernetes, Intel, or Networking
       requiring fresh documentation, set intent to "technical" and provide
       a refined search_query.
    """
    
    with logfire.span("🧠 Planner Decision"):
        decision : PlannerDecision = structured_llm.invoke(prompt)
        logfire.info(f"Intent identified: {decision.intent}")
    
    if decision.intent == "conversational":
        return {
            "current_query": "CONVERSATIONAL",
            "status": "Handling conversationally (using memory)...",
            "plan": ["Intent: Conversational/Memory", "Retrieval: Skipped"]
        }
    
    search_query=decision.search_query or user_message
    return {
        "current_query": search_query,
        "status": f"Technical research needed. Searching for: {search_query}",
        "plan": ["Intent: Technical", f"Search Term: {search_query}",f"reason:{decision.reasoning}"]
    }

    
