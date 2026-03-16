import random
from storage import load_classes

def generate_group(classes):
    print("Classes")
    for c in classes:
        print("-", c)

    class_name = input("Select Class--> ").title().strip()

    if class_name not in classes:
        print("Class not found...")
        return

    students = classes[class_name]
    present_students = []
    for student in students:
        if students["status"]:
            present_students.append(students["name"])

    random.shuffle(present_students)

    group_size = 2
    groups = []

    for i in range(0, len(present_students), group_size):
        group = present_students[i:i+group_size]
        groups.append(group)
    
    for i, group in enumerate(groups, start=1):
        print(f"\nGroup {i}")
        for student in group:
            print("-", student)


