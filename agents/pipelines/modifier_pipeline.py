import logging
import os
import json
from typing import Optional, List, Dict
import dspy
from pathlib import Path

from agents.modules.visualizer import VisualizerAgent

class ModifierPipeline:
    def __init__(self):
        self.visualizer: Optional[VisualizerAgent] = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the pipeline components"""
        if self.is_initialized:
            print("[INFO] Modifier pipeline already initialized")
            return
            
        try:
            print("[INFO] Initializing modifier pipeline...")
            
            # Initialize DSPy configuration
            self._initialize_dspy()
            
            # Initialize visualizer agent
            self.visualizer = VisualizerAgent()
            
            self.is_initialized = True
            print("[INFO] Modifier pipeline initialization complete")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize modifier pipeline: {str(e)}")
            raise
            
    def _initialize_dspy(self):
        """Initialize DSPy configuration"""
        # Disable logging
        dspy.disable_litellm_logging()
        dspy.disable_logging()
        loggers = ["LiteLLM Proxy", "LiteLLM Router", "LiteLLM"]
        for logger_name in loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.CRITICAL + 1)

        # Configure DSPy with the language model
        model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_BASE_URL")

        if not api_key:
            raise ValueError("[ERROR] OPENAI_API_KEY not set in .env file")

        print(f"[INFO] Initializing DSPy with model: {model_name}")
        
        lm = dspy.LM(
            model=model_name,
            api_key=api_key,
            api_base=api_base if api_base else None
        )
        dspy.configure(lm=lm)
            
    async def modify_visualization(
        self, 
        prompt: str, 
        task: str, 
        file_path: str, 
        original_json_data: str,
        original_png_path: str,
        conversation_history: List[Dict[str, str]] = None
    ):
        """
        Modify an existing visualization based on the provided data and prompt
        
        Args:
            prompt: The user's prompt
            task: The current task
            file_path: Path to the new data file
            original_json_data: JSON data of the original visualization
            original_png_path: Path to the original PNG image
            conversation_history: List of previous conversation messages
            
        Returns:
            Dictionary containing:
                - success: Boolean indicating success
                - fig_json: JSON representation of the modified figure
                - output_png_path: Path to the modified PNG image
                - error: Error message if any
        """
        if not self.is_initialized:
            raise RuntimeError("Modifier pipeline not initialized. Call initialize() first")
            
        if conversation_history is None:
            conversation_history = []
            
        try:
            print(f"\n=== Modifying visualization for task: {task} ===")
            print(f"Original visualization: {original_png_path}")
            print(f"New data file: {file_path}")
            
            # Create output directory if it doesn't exist
            os.makedirs(os.getenv('VISUALIZATION_RESULTS_DIR'), exist_ok=True)
            
            # Generate a unique output path for the modified visualization
            file_name = Path(file_path).name
            output_png_path = f"{os.getenv('VISUALIZATION_RESULTS_DIR')}/modified_{file_name}.png"
            
            # Add context about the original visualization to the prompt
            enhanced_prompt = f"""
{prompt}

Please modify the visualization based on the new data. 
The original visualization is available at: {original_png_path}
The original visualization data: {original_json_data}
"""
            
            # Generate the modified visualization
            fig_json = self.visualizer.visualize_by_prompt(
                prompt=enhanced_prompt,
                task=task,
                file_path=file_path,
                output_png_path=output_png_path,
                conversation_history=conversation_history
            )
            
            print(f"[INFO] Successfully modified visualization")
            
            return {
                "success": True,
                "fig_json": fig_json,
                "output_png_path": output_png_path
            }
            
        except Exception as e:
            error_msg = f"Failed to modify visualization: {str(e)}"
            import traceback
            traceback.print_exc()
            print(f"[ERROR] {error_msg}")
            return {
                "success": False,
                "error": error_msg
            } 