from dotenv import load_dotenv
import asyncio
from typing import List
from agents.pipelines.visualization_pipeline import VisualizationPipeline
from agents.pipelines.analysis_pipeline import AnalysisPipeline

                        
async def main(prompts: List[str]):
    # Load environment variables
    load_dotenv()
    
    # Initialize pipeline
    pipeline = VisualizationPipeline()
    await pipeline.initialize()
    
    results = []
    img_paths = []
    for prompt in prompts:
        print(f"\n{'='*50}")
        print(f"Processing prompt: {prompt}")
        print(f"{'='*50}")
        
        result = await pipeline.generate_visualization(prompt)
        results.append(result)
        
        print("Done generating visualization")
        
        # get the output png file path for analysis later
        img_paths.append(result["output_png_path"])
        
    
    # Initialize analysis pipeline
    analysis_pipeline = AnalysisPipeline()
    await analysis_pipeline.initialize()
    
    print("Done initializing analysis pipeline")
    
    # Analyze the images
    analysis = await analysis_pipeline.analyze_figures(img_paths, prompts)
    print("Done analyzing figures")
    return results, analysis

if __name__ == "__main__":
    # Example prompts
    test_prompts = [
        "Is Ethereum suitable to invest right now?",
        # Add more test prompts here
    ]
    
    # Run the async main function
    asyncio.run(main(test_prompts))
