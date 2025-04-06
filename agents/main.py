from dotenv import load_dotenv
import dspy
import os
import asyncio
from typing import List, Dict, Optional
from agents.pipelines.visualization_pipeline import VisualizationPipeline
from agents.pipelines.analysis_pipeline import AnalysisPipeline
from agents.pipelines.modifier_pipeline import ModifierPipeline
from agents.modules.router import ActionRouter, ACTION_LIST
from agents.modules.webhook_monitor import WebhookMonitorAgent

async def main(
    prompt: str, 
    conversation_history: List[Dict[str, str]] = None,
    mentioned_visualizations: Optional[List[Dict]] = None
):
    # Load environment variables
    load_dotenv()
    
    if conversation_history is None:
        conversation_history = []
    
    if mentioned_visualizations is None:
        mentioned_visualizations = []
    
    print(f"Processing prompt with {len(mentioned_visualizations)} mentioned visualizations")
    
    model = f"openai/{os.getenv('OPENAI_MODEL')}"
    lm = dspy.LM(model=model, api_key=os.getenv("OPENAI_API_KEY"))
    dspy.configure(lm=lm)
    
    # Initialize pipelines and agents
    analysis_pipeline = AnalysisPipeline()
    await analysis_pipeline.initialize()
        
    visualization_pipeline = VisualizationPipeline()
    await visualization_pipeline.initialize() 
    
    modifier_pipeline = ModifierPipeline()
    await modifier_pipeline.initialize()
    
    webhook_agent = WebhookMonitorAgent()
    await webhook_agent.initialize_tools()
    
    # Add available mcp tools in visualization pipeline to the prompt
    prompt = prompt + "\n\nAvailable MCP tools in RETRIEVE_AND_VISUALIZE_INFORMATION: " + ", ".join([tool.name for tool in visualization_pipeline.retriever.tools])
    
    # Add available mcp tools in webhook agent to the prompt
    prompt = prompt + "\n\nAvailable MCP tools in USE_WEBHOOK: " + ", ".join([tool.name for tool in webhook_agent.tools])
    
    # Add information about mentioned visualizations to the prompt if any
    if mentioned_visualizations and len(mentioned_visualizations) > 0:
        viz_info = "The user has referenced the following visualizations:\n"
        for i, viz in enumerate(mentioned_visualizations):
            viz_info += f"Visualization {i+1} (ID: {viz['visualization_id']}): {viz['png_path']}\n"
        prompt = prompt + "\n\n" + viz_info
    
    # Initialize router with predict
    router = dspy.Predict(ActionRouter)
    
    # Get route action with required fields
    response = router(
        available_action=ACTION_LIST,
        conversation_history=conversation_history,    
        new_message=prompt,
        mentioned_visualizations=mentioned_visualizations
    )
    
    # Get action and parameters from response
    action = response.action
    parameters = response.parameters
    
    print("action: ", action)
    print("parameters: ", parameters)
    
    # Execute action
    if action == "ANALYZE_GRAPH":
        # If we have mentioned visualizations, use their paths
        img_paths = parameters.get("img_paths", [])
        if mentioned_visualizations and len(mentioned_visualizations) > 0:
            img_paths = [viz["png_path"] for viz in mentioned_visualizations]
            print(f"Using mentioned visualization paths: {img_paths}")
        
        results = await analysis_pipeline.analyze_figures(img_paths, prompt, conversation_history)
        results["action"] = action
    elif action == "RETRIEVE_AND_VISUALIZE_INFORMATION":
        results = {"visualization_results_list": []}
        for info_needed in parameters["information_needed"]:
            result = await visualization_pipeline.generate_visualization(info_needed, conversation_history)
            results["visualization_results_list"].append(result)
        results["action"] = action
    elif action == "MODIFY_VISUALIZATION":
        # This action is for modifying existing visualizations
        results = {"modification_results_list": []}
        
        # Check if we have mentioned visualizations
        if not mentioned_visualizations or len(mentioned_visualizations) == 0:
            # If no visualizations are mentioned, return an error
            results["success"] = False
            results["error"] = "No visualizations mentioned to modify"
            results["action"] = action
            return results
        
        for viz_to_modify in mentioned_visualizations:            
            # Modify the visualization
            result = await modifier_pipeline.modify_visualization(
                prompt=prompt,
                task=prompt,
                file_path=viz_to_modify["file_path"],
                original_json_data=viz_to_modify["json_data"],
                original_png_path=viz_to_modify["png_path"],
                conversation_history=conversation_history
            )

            # Add the result to the modification results list
            if result["success"]:
                results["modification_results_list"].append({
                    "success": True,
                    "visualization_id": viz_to_modify["visualization_id"],
                    "fig_json": result["fig_json"],
                    "output_png_path": result["output_png_path"],
                    "file_path": viz_to_modify["file_path"],
                })
            else:
                results["modification_results_list"].append({
                    "success": False,
                    "error": result.get("error", "Unknown error")
                })
        results["action"] = action
    elif action == "USE_WEBHOOK":
        # Handle webhook tool usage
        results = {"webhook_results": None}
        result = await webhook_agent.execute_tool_by_prompt(prompt)
        results["webhook_results"] = result
        results["action"] = action
    else:
        # GENERAL_CHAT
        # return the message generated by the AI
        results = {"message": parameters["message"]}
        results["action"] = action
    return results
        
if __name__ == "__main__":
    prompts = [
        "Compare the protocol and token profit and loss for this wallet address on Arbitrum mainnet: 0x8a7fd3eb9e41b3dd1b37f853b7a5252c59a782fd",
        # "Hello",
        # "Analyze img_path: 'data/visualization_results/20250405_183413_0xf3be3c8afc0fc1c91d9a365b36cee5bb5acd74f1_get_bal.json.png', analyze how is this portfolio doing?"
    ]
    for prompt in prompts:
        print(f"\n=== Testing prompt: {prompt} ===")
        response = asyncio.run(main(prompt))
        print(f"Response: {response}")
