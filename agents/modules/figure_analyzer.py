import base64
from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

class FigureAnalyzerAgent:
    def __init__(self):
        self.client = OpenAI()

    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def analyze_figures(
        self, image_paths: list[str], prompt: str = "Please analyze the figure and provide a detailed description of the figure.",
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Analyze multiple images using OpenAI Vision API

        Args:
            image_paths: List of paths to image files
            prompt: Custom prompt for analysis
            conversation_history: List of previous conversation messages
        """
        if conversation_history is None:
            conversation_history = []
            
        # Create messages list starting with conversation history
        messages = []
        if conversation_history:
            # Add relevant context from conversation history
            context = "Previous conversation context:\n"
            for msg in conversation_history[-3:]:  # Only use last 3 messages for context
                role = "User" if msg["role"] == "user" else "Assistant"
                context += f"{role}: {msg['content']}\n"
            prompt = f"{context}\n\nBased on this context, {prompt}"

        # Create message content starting with the text prompt
        content = [{"type": "text", "text": prompt}]

        # Add each image to the content
        for image_path in image_paths:
            base64_image = self.encode_image(image_path)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                }
            )

        # Add the content to messages
        messages.append({"role": "user", "content": content})

        response = self.client.chat.completions.create(
            model=os.getenv("MODEL_NAME"),
            messages=messages,
            max_tokens=1000,
        )
        return response.choices[0].message.content
