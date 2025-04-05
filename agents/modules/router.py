import dspy
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


class ToolBase(BaseModel):
    """Base model for tool"""


def convert_to_schema(model: ToolBase) -> Dict[str, Any]:
    json_schema = model.model_json_schema()
    function_calling_json = {
        "type": "function",
        "function": {
            "name": model.__name__,
            "description": model.__doc__,
            "parameters": json_schema,
        },
    }
    return function_calling_json


class ANALYZE_GRAPH(ToolBase):
    """Analyze the graph based on user's query, trigger when user's query is about analyzing the graph provided"""
    
    img_paths: list[str] = Field(
        ...,
        description="The paths of the images to analyze",
    )
    aspect_to_cover: str = Field(
        ..., description="The aspect to cover in the analysis based on the user's query"
    )


class RETRIEVE_AND_VISUALIZE_INFORMATION(ToolBase):
    """Retrieve information based on user's query, trigger when retrieving more information can be beneficial to answer the user's query.
    For example:
    - User's query: "Is Uniswap hot in the past week?"
    - The information needed to be retrieved: "The transaction volume of Uniswap in the past week"
    """

    information_needed: list[str] = Field(
        ...,
        description="The information needed to be retrieved to answer the user's query",
    )


class MODIFY_VISUALIZATION(ToolBase):
    """Modify an existing visualization based on new data, trigger when the user wants to update or modify a visualization they've referenced.
    For example:
    - User's query: "Can you update this visualization with the latest data?"
    - The file path for the new data: "path/to/new/data.json"
    """

    file_path: str = Field(
        ...,
        description="The path to the new data file to use for modifying the visualization",
    )
    task: str = Field(
        ...,
        description="The specific task for modifying the visualization",
    )


class GENERAL_CHAT(ToolBase):
    """General chat, trigger when user's query is a general message that does not related to crypto or web 3"""

    message: str = Field(..., description="The message to reply to the user")


ACTION_LIST = [
    convert_to_schema(tool)
    for tool in [
        ANALYZE_GRAPH,
        RETRIEVE_AND_VISUALIZE_INFORMATION,
        MODIFY_VISUALIZATION,
        GENERAL_CHAT,
    ]
]

class ActionRouter(dspy.Signature):
    """
    # Objective
    1. Figure out the best action to take based on the user's latest message.
    2. If the user prompt you to do something but you dont have enough information to use the tool you want to use, you should ask for more information using GENERAL_CHAT.
    3. If the user has referenced specific visualizations, consider using ANALYZE_GRAPH to analyze those visualizations.
    4. If the user wants to modify a visualization they've referenced, use MODIFY_VISUALIZATION.
    """

    available_action = dspy.InputField(description="List of actions you can take")
    conversation_history = dspy.InputField(description="Conversation history")
    new_message = dspy.InputField(description="Latest message from the user")
    mentioned_visualizations = dspy.InputField(
        description="List of visualizations mentioned by the user, each containing visualization_id, png_path, and json_data"
    )
    action = dspy.OutputField(description="Action to take")
    parameters: dict[str, Any] = dspy.OutputField(
        description="Parameters for the action"
    )
    
class ActionRouterAgent:
    def __init__(self, engine=None) -> None:
        self.engine = engine
        self.action_router = dspy.Predict(ActionRouter)
        
    def route_action(
        self, 
        available_action: list[str], 
        conversation_history: list[dict], 
        new_message: str,
        mentioned_visualizations: Optional[List[Dict]] = None
    ) -> tuple[str, dict]:
        """Route the action to take based on the user's latest message."""
        if mentioned_visualizations is None:
            mentioned_visualizations = []
            
        route_action = self.action_router(
            available_action=available_action,
            conversation_history=conversation_history,
            new_message=new_message,
            mentioned_visualizations=mentioned_visualizations
        )
        return route_action.action, route_action.parameters
