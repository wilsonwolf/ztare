import json
import re

def parse_llm_json(raw_text):
    clean_text = raw_text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:-3]
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:-3]
    clean_text = clean_text.strip()
    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        # Attempt to repair truncated JSON by closing open strings/objects/arrays
        repaired = clean_text
        # Close any unterminated string
        if repaired.count('"') % 2 != 0:
            repaired += '"'
        # Close open brackets/braces
        open_braces = repaired.count('{') - repaired.count('}')
        open_brackets = repaired.count('[') - repaired.count(']')
        repaired += ']' * max(0, open_brackets)
        repaired += '}' * max(0, open_braces)
        return json.loads(repaired)