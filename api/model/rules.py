

def returnModelRules():
    return """
     Weekly Schedule: The schedule you generate will repeat weekly unless told otherwise.
    Fixed School Schedule:
    It is always active and cannot be moved.
    school tasks that are imported from the given data must only be scheduled between 8:00 or mostly 8:30 AM and 4:00 PM (for school-related tasks only if the data seems untruth fix it only for the time slots).
    school tasks are important and must be always included
    'EMPTY CELL' are referring to empty time slot usually a one hour so if you see one pass one hour starting 8:00am and so on
    school tasks that are imported from the given data are fixed and can't be moved
    Data Correction:
    If a task is given at an invalid time (like 2 AM for school work), adjust it to a valid slot (e.g. 10 AM) within the allowed hours.
    User Preferences:
    Prioritize user-specified preferred times when placing tasks.
    High-priority tasks go first in the day or to preferred slots.
    Avoid Overlap:
    Tasks should not conflict with school time or each other.
    if a school cell is empty you can use it for other tasks as long as it doesn't have another class after it unless the task is something that can be done anywhere.
    you can use the days the schedule doesn't use too like friday
"""