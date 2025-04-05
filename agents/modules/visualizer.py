# TODO: python plotly with python interpreter


import dspy
import pandas as pd
import kaleido
import re

class Visualizer(dspy.Signature):
    """
    You are a visualization expert in python plotly. 
    You are given a user's prompt and a json data file. 
    You need to plot the data in the json file using python plotly. 
    Read the data from the json file and plot the data using python plotly. 
    Remember, do not directly use the sample data of the json file, you need to read the data from the json file. 
    Do not assume what the data is, always read the data from the json file. You can refer to sample data for the structure of the data.
    
    Rules:
    1. Always check what data is available in the json file. The sample data is given to you.
    2. Only use columns that are available in the data! Avoid keyerror!
    3. When u plot wallet address or contract address, only show the first 4 and last 4 characters, with ellipsis in the middle because they are too long.
    4. No need to use fig.show() in the plot code, just return the plot code.
    4. If the data is token balances or similar, you should get the decimals of the contract from the data and then convert the balance to the token's decimal so that the visualization scale is easier to understand.
    4. If there are timestamp data in the json data and you want to use it, you should convert the timestamp to a human readable date and time, remember to use unit='s' when converting the timestamp to a datetime object.
    """

    prompt = dspy.InputField(prefix="User's prompt:")
    task = dspy.InputField(prefix="The current task split from the user's prompt:")
    file_path = dspy.InputField(prefix="The file path of the json data:")
    sample_data = dspy.InputField(prefix="The sample data of the json file:")
    reasoning = dspy.OutputField(
        prefix="Which information should be visualized based on the user's prompt?"
    )
    plot_code: str = dspy.OutputField(prefix="The plot python plotly code:")


class VisualizerAgent:
    def __init__(self, engine=None) -> None:
        self.engine = engine
        self.visualize = dspy.Predict(Visualizer, max_tokens=16000)
        
    def visualize_by_prompt(
        self, prompt: str, task: str, file_path: str, output_png_path: str
    ):
        
        # overwrite the default json.loads to use pandas.json_normalize so that large int can be read
        import simplejson
        pd.io.json._json.loads = lambda s, *a, **kw: simplejson.loads(s)
        pd.io.json._json.ujson_loads = lambda s, *a, **kw: simplejson.loads(s)
        # pd.io.json._json.loads = lambda s, *a, **kw: pd.json_normalize(simplejson.loads(s))
        # pd.io.json._json.ujson_loads = lambda s, *a, **kw: pd.json_normalize(simplejson.loads(s))
        
        df = pd.read_json(file_path)
        sample_data = df.head(5)
        
        print(f"The sample data: {sample_data}")
        print(f"The column names: {sample_data.columns}")
        
        response = self.visualize(
            prompt=prompt,
            task=task,
            file_path=file_path,
            sample_data=sample_data,
        )
        plot_code = response.plot_code
        print(f"[DEBUG] Generated plot code:\n{plot_code}")
        
        # Clean up the code - remove markdown code blocks if present
        plot_code = re.sub(r"```python\s*", "", plot_code)
        plot_code = re.sub(r"```\s*", "", plot_code)
        
        try:
            # Create a new namespace with all required imports
            import plotly.graph_objects as go
            import json
            
            namespace = {
                'pd': pd,
                'json': json,
                'go': go,
                'file_path': file_path  # Also provide the file path
            }
            
            # append this to the point after the imports in the plot_code
            # find the point after the imports in the plot_code
            # imports_index = plot_code.find("import")
            # if imports_index != -1:
            #     plot_code_before_imports = plot_code[:imports_index]
            #     plot_code_after_imports = plot_code[imports_index:]
                
            # print(f"The plot code before imports: {plot_code_before_imports}")
            # print(f"The plot code after imports: {plot_code_after_imports}")
            
            # PD_JSON_OVERWRITE_CODE = """\nimport simplejson; pd.io.json._json.loads = lambda s, *a, **kw: simplejson.loads(s); pd.io.json._json.ujson_loads = lambda s, *a, **kw: simplejson.loads(s);\n"""
            # PD_JSON_OVERWRITE_CODE = """\nimport simplejson; pd.io.json._json.loads = lambda s, *a, **kw: pd.json_normalize(simplejson.loads(s)); pd.io.json._json.ujson_loads = lambda s, *a, **kw: pd.json_normalize(simplejson.loads(s));\n"""
            # plot_code = plot_code_before_imports + PD_JSON_OVERWRITE_CODE + plot_code_after_imports
            
            # Execute the code in the namespace
            exec(plot_code, namespace)
            
            # Get the figure from the namespace
            if 'fig' not in namespace:
                raise ValueError("Plot code did not create a 'fig' variable")
            
            fig = namespace['fig']
            print("[INFO] Successfully created plotly figure")
            
            # Convert to JSON
            fig_json = fig.to_json()
            print("[INFO] Successfully converted figure to JSON")
            
            # Save the figure to the output png path
            fig.write_image(output_png_path)
            print(f"[INFO] Successfully saved figure to {output_png_path}")
            
            return fig_json
            
        except Exception as e:
            print(f"[ERROR] Failed to create plot: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"[ERROR] Plot code that failed:\n{plot_code}")
            raise


# Run a quick test
if __name__ == "__main__":
    json_filepath = "data/retriever_results/20250405_021246_get_balance_0x1f9090aaE28b8a3dCeaDf281B0F12828e676.json"
    visualizer = VisualizerAgent(
        prompt="Is Ethereum suitable to invest right now?",
        task="Retrieve the current price and historical price trends of Ethereum.",
        file_path=json_filepath,
        output_png_path="data/visualization_results/20250405_021246_get_balance_0x1f9090aaE28b8a3dCeaDf281B0F12828e676.png"
    )
