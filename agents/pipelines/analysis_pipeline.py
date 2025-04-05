import dspy
import logging
from typing import Optional, List, Dict
from agents.modules.figure_analyzer import FigureAnalyzerAgent

class AnalysisPipeline:
    def __init__(self):
        self.figure_analyzer: Optional[FigureAnalyzerAgent] = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the pipeline components"""
        if self.is_initialized:
            print("[INFO] Pipeline already initialized")
            return
            
        try:
            print("[INFO] Initializing analysis pipeline...")
            
            # Initialize DSPy configuration
            self._initialize_dspy()
            
            # Initialize agents
            self.figure_analyzer = FigureAnalyzerAgent()
            
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
        
    async def analyze_figures(self, image_paths: list[str], prompt: str = "Please analyze the figure and provide a detailed description of the figure.", conversation_history: List[Dict[str, str]] = None):
        """Analyze multiple images using OpenAI Vision API"""
        if not self.is_initialized:
            raise RuntimeError("Pipeline not initialized. Call initialize() first")
            
        if conversation_history is None:
            conversation_history = []
        
        try:
            print(f"\n=== Analyzing figures for prompt: {prompt} ===")
            print(f"Conversation history: {conversation_history}")
            
            # Call the analysis function with conversation history    
            analysis = self.figure_analyzer.analyze_figures(image_paths, prompt, conversation_history)
            print(f"[INFO] Analysis complete: {analysis}")
            
            return {
                "analysis": analysis
                }
        
        except Exception as e:
            error_msg = f"Failed to analyze figures: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }