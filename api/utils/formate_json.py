import json
import re

def extract_json_array_from_response(response: dict) -> list:
    try:
        # Step 1: Extract the raw markdown content
        raw_text = response["candidates"][0]["content"]["parts"][0]["text"]

        # Step 2: Match JSON array block inside ```json ... ```
        match = re.search(r'```json\s*(\[\s*{.*?}\s*\])\s*```', raw_text, re.DOTALL)
        if not match:
            raise ValueError("JSON array block not found in the response.")

        json_str = match.group(1)

        # Step 3: Clean and parse the JSON array
        cleaned = re.sub(r'[\x00-\x1f\x7f]', '', json_str)  # Remove unwanted control characters
        return json.loads(cleaned)

    except Exception as e:
        print("Error extracting JSON array:", str(e))
        return []
