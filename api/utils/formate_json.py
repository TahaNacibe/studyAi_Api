import json
import re

def extract_json_from_response(response: dict) -> dict:
    try:
        # Step 1: Extract the raw markdown content
        raw_text = response["candidates"][0]["content"]["parts"][0]["text"]

        # Step 2: Extract content inside ```json ... ```
        match = re.search(r'```json\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
        if not match:
            raise ValueError("JSON block not found in the response.")

        json_str = match.group(1)

        # Step 3: Clean the string to remove bad control characters
        cleaned = re.sub(r'[\x00-\x1f\x7f]', '', json_str)  # Remove control characters
        return json.loads(cleaned)

    except Exception as e:
        print("Error extracting JSON:", str(e))
        return {}
