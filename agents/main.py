import dspy
from dotenv import load_dotenv
import os
import logging
import pandas as pd
from agents.modules.planner import Planner
from agents.modules.retriever import MCPRetrieverAgent

dspy.disable_litellm_logging()
dspy.disable_logging()
loggers = ["LiteLLM Proxy", "LiteLLM Router", "LiteLLM"]

for logger_name in loggers:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.CRITICAL + 1)

load_dotenv()


lm = dspy.LM(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    api_base=os.getenv("OPENAI_BASE_URL"),
)
dspy.configure(lm=lm)


def generate_visualization_by_prompt(prompt: str):
    # planner = Planner()
    # tasks = planner.split_task_by_prompt(prompt)
    results = []
    # print(f"The list of tasks:")
    # for idx, task in enumerate(tasks):
    #     print(f"  {idx+1}. {task}")
        
    # print()
    tasks = [prompt]
    
    for task in tasks:
        print(f"Retrieving data for task: {task}")
        retriever = MCPRetrieverAgent()
        answer = retriever.retrieve_by_prompt(task)
        results.append(answer)
        print(f"Answer: {answer}")

    return results


def main():
    prompt = "get balance 0x1f9090aaE28b8a3dCeaDf281B0F12828e676c326"
    results = generate_visualization_by_prompt(prompt)
    print(results)


if __name__ == "__main__":
    main()
