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
        if student["status"]:
            present_students.append(student["name"])

    random.shuffle(present_students)
    print("1. Group sizes")
    print("2. Group total")
    choice = input(">")
    try:
        choice = int(choice)
    except ValueError:
        print("ValueError")
        return
    if choice == 1:
        while True:
            group_size = input("how many per group -> ")
            try:
                group_size = int(group_size)
            except ValueError:
                print("ValueError")
                return
            
            groups = []

            for i in range(0, len(present_students), group_size):
                group = present_students[i:i+group_size]
                groups.append(group)
            
            for i, group in enumerate(groups, start=1):
                print(f"\nGroup {i}")
                for student in group:
                    print("-", student)

    elif choice == 2:
        while True:
            num_groups_input = input("How many groups--> ")

            try:
                num_groups = int(num_groups_input)
            except ValueError:
                print("Enter a number...")

            if num_groups <= 0:
                print("Must be > 0")
                continue

            if num_groups > len(present_students):
                print("More groups than students? Really?")
                continue

            groups = [[] for _ in range(num_groups)]

            for i, student in enumerate(present_students):
                groups[i % num_groups].append(student)

            
            for i, group in enumerate(groups, start=1):
                print(f"\nGroup {i}")
                for student in group:
                    print("-", student)

