import json

def save_students(student_list):
    with open ("students.json", "w") as file:
        json.dump(student_list, file, indent=4)

def load_students():
    try:
        with open ("students.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return[]
    
def save_classes(classes):
    with open ("classes.json", "w") as file:
        json.dump(classes, file, indent=4)
    print("Classes Saved")

def load_classes():
    try:
        with open("classes.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return{}

def save_groups(class_name, groups):
    filename = f"{class_name}_groups.json"

    data = {
        "class": class_name,
        "groups": groups
    }

    try:
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving groups: {e}")