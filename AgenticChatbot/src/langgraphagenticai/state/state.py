from typing_extensions import TypedDict
from typing import Annotated, List, Dict, Any
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[List, add_messages]

    frequency: str
    news_data: List[Dict[str, Any]]
    summary: str
    filename: str