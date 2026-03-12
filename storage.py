import json

def save_students(student_list):
    with open ("students.json", "w") as file:
        json.dump(student_list, file, indent=4)

def load_students():
    try:
        with open ("student.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return[]
    
def save_classes(classes):
    with open ("classes.json", "w") as file:
        json.dumb(classes, file, indent=4)
    print("Classes Saved")