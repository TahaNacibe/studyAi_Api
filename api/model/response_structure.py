


def getResponseStructure():
    return """
   You are to generate a JSON array of schedule items ready to be inserted into the Supabase table `schedule_items`.

    Each object must include the following fields:
    - title: string (name of the task)
    - start_time: string in "HH:MM" 24-hour format
    - end_time: string in "HH:MM" 24-hour format
    - event_type: string (e.g., "study", "personal", "workout)
    - event_day: string (e.g., "Monday", "Tuesday", etc.)
    - priority: string ("1", to "5") 
    - color: string (optional, e.g., "#F87171" for red, or derive from priority if needed)
    - user_id: keep it null (return the world Null)
    - module_id: Keep it Null (return the world Null)

    Return only a **JSON array**, not an object grouped by day.

    ---

    Breaks have also a item with event type break
    Example Response:

    ```json
    [
    {
        "title": "Math Class",
        "start_time": "08:00",
        "end_time": "10:00",
        "event_type": "school",
        "event_day": "Monday",
        "color": "#3B82F6",
        "user_id": null,
        "module_id": null
    },
    {
        "title": "Workout",
        "start_time": "16:30",
        "end_time": "18:00",
        "event_type": "personal",
        "event_day": "Monday",
        "color": "#10B981",
        "user_id": null,
        "module_id": null
    },
    {
        "title": "English Homework",
        "start_time": "10:00",
        "end_time": "11:30",
        "event_type": "study",
        "event_day": "Tuesday",
        "color": "#FBBF24",
        "user_id": null,
        "module_id": null
    }
    ]


"""