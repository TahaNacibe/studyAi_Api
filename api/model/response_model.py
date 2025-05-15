import requests
from api.model.prompt import createSystemPrompt
from api.utils.formate_json import extract_json_from_response
from backend.settings import GEMINI_API_KEY 


url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

def getResponseFromEndPoint(tableData, userClass, userTasks, preferences, modelsAndTasksPriorities):
    payload = {
    "contents": [
        {
        "role":"user",
        "parts": [
            {
            "text": createSystemPrompt(tableData, userClass, userTasks, preferences, modelsAndTasksPriorities)
            }
        ]
        }
    ]
    }
    headers = {"Content-Type": "application/json"}
    
    
    #? apply actual request
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        formatted_json = extract_json_from_response(response.json())
        return formatted_json
    else:
        return f"Error: {response.status_code}"