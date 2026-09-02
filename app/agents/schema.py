from pydantic import BaseModel, Field
from typing import Literal, Optional

class PlannerDecision(BaseModel):
    intent: Literal["conversational", "technical"] = Field(
        description="Classify as 'conversational' (greetings, chit-chat, memory recall) or 'technical' (requires documentation search)."
    )
    search_query: Optional[str] = Field(
        default=None,
        description="The refined, standalone search query for the vector database. None if intent is conversational."
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Brief justification for the routing decision."
    )
