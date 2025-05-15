


def getResponseStructure():
    return """
    {
        dayName:[
            {
                "task_name": "Task",
                "start_time": "hh:mm",
                "end_time": "hh:mm",
                "category": "type School or work or ...",
                "priority": "3 or 2 or 1"
            },
            ...continue like that for other tasks then so for other days
        ]
    }
    
    
    Response Structure:
    Output only a JSON object, grouped by days.
    Each day ("Monday", "Tuesday", etc.) is a key mapping to a list of task objects.

    Each task object must include:

    task_name: string

    start_time: string (24h format, e.g. "14:00")

    end_time: string

    category: string (e.g. "school", "study", "personal")

    priority: "1", "2", or "3"
    
    Example of the return :{
    "Monday": [
        {
        "task_name": "Math Class",
        "start_time": "08:00",
        "end_time": "10:00",
        "category": "school",
        "priority": "high"
        },
        {
        "task_name": "Workout",
        "start_time": "16:30",
        "end_time": "18:00",
        "category": "personal",
        "priority": "medium"
        }
    ],
    "Tuesday": [
        {
        "task_name": "English Homework",
        "start_time": "10:00",
        "end_time": "11:30",
        "category": "study",
        "priority": "high"
        }
    ]
}

"""