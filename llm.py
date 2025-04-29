import os
import json
from google import genai
from google.genai import types
from utils import extract_json


class GeminiBot:
    def __init__(self, context, model="gemini-2.0-flash"):
        self.model = model
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.system_instruction = """You are an assistant that answers questions based only on the provided context.

# Instructions:
1. If the question can be answered using the context, provide a clear and concise answer.
2. If the question cannot be answered using the context, respond with "I cannot answer this question based on the provided context."
3. For every answer, provide the source of the context (documentation url) from which the context for the prompt is retrieved.
4. Do not use information outside of the given context.
5. Do not make up information.
6. DO NOT start your responses with phrases like "Based on the provided context," or "According to the context," or similar phrases.
"""
        context_with_instruction = f"{self.system_instruction}\n\n# Context:\n{context}"     
        self.cache = self.client.caches.create(
            model=self.model,
            config=types.CreateCachedContentConfig(
                display_name='context',
                contents=[context_with_instruction],
                ttl="3600s",
            )
        )
    
    def query(self, prompt, return_json=False):
        try:
            response = self.client.models.generate_content(
                model=self.model,
                config=types.GenerateContentConfig(
                    cached_content=self.cache.name,
                    temperature=0.2,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=8192,
                ),
                contents=prompt
            )
            
            text = response.text
            if return_json:
                json_data = extract_json(text)
                if json_data:
                    return json_data
            return text
        except Exception as e:
            print(f"Error querying Gemini: {e}")
            raise
    
    def update_context(self, new_context):
        context_with_instruction = f"{self.system_instruction}\n\n# Context:\n{new_context}"
        
        self.cache = self.client.caches.create(
            model=self.model,
            config=types.CreateCachedContentConfig(
                display_name='context',
                contents=[context_with_instruction],
                ttl="3600s",
            )
        )


if __name__ == "__main__":
    
    prompt = "How can I view my deployed job?"
    with open("src/data/data.json", "r") as f:
        data = json.load(f)
    context = json.dumps(data)
    llm = GeminiBot(context)
    
    response = llm.query(prompt)
        