import os
import re

def extract_json(text):
    if not text:
        return None  
    pattern = r'```json\s*(.*?)\s*```|(\{[\s\S]*\})'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1) or match.group(2).strip()
    return None
