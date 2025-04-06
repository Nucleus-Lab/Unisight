import logging
import os
from typing import Optional, List, Dict
import dspy
from pathlib import Path

from agents.modules.retriever import MCPRetrieverAgent
from agents.modules.visualizer import VisualizerAgent

class VisualizationPipeline:
    def __init__(self):
        self.retriever: Optional[MCPRetrieverAgent] = None
        self.visualizer: Optional[VisualizerAgent] = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the pipeline components"""
        if self.is_initialized:
            print("[INFO] Pipeline already initialized")
            return
            
        try:
            print("[INFO] Initializing visualization pipeline...")
            
            # Initialize DSPy configuration
            self._initialize_dspy()
            
            # Initialize agents
            self.retriever = MCPRetrieverAgent()
            await self.retriever.initialize_tools()
            self.visualizer = VisualizerAgent()
            
            self.is_initialized = True
            print("[INFO] Pipeline initialization complete")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize pipeline: {str(e)}")
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
            
    async def generate_visualization(self, prompt: str, conversation_history: List[Dict[str, str]] = None):
        """Generate visualization for a given prompt"""
        if not self.is_initialized:
            raise RuntimeError("Pipeline not initialized. Call initialize() first")
            
        if conversation_history is None:
            conversation_history = []
            
        try:
            print(f"\n=== Retrieving data for task: {prompt} ===")
            result = await self.retriever.retrieve_by_prompt(prompt, conversation_history)
            
            if result.get("file_path"):
                # extract filename from the file path
                file_name = Path(result["file_path"]).name
                # build the output png file path
                os.makedirs(os.getenv('VISUALIZATION_RESULTS_DIR'), exist_ok=True)
                output_png_path = f"{os.getenv('VISUALIZATION_RESULTS_DIR')}/{file_name}.png"
                result["output_png_path"] = output_png_path
            
            if result["success"]:
                fig_json = self.visualizer.visualize_by_prompt(prompt, prompt, result["file_path"], output_png_path, conversation_history)
                print(f"[INFO] Successfully generated visualization")
                result["fig_json"] = fig_json
            else:
                print(f"[ERROR] Failed to retrieve data: {result.get('error', 'Unknown error')}")
        
            print("result in generate_visualization: ", result)
            return result    
        except Exception as e:
            error_msg = f"Failed to generate visualization: {str(e)}"
            import traceback
            traceback.print_exc()
            print(f"[ERROR] {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }