from storage import load_classes, save_classes
from Classes import create_class, rename_class, remove_class
from student_manage import manage_students
from group_gen import generate_group

def main():
    classes = load_classes()

    while True:
        print("\n1. Create Class")
        print("2. Manage Class Students")
        print("3. Rename Class")
        print("4. Remove Class")
        print("5. Generate Group")
        print("6. Exit")

        choice = input("->")
        try:
            choice = int(choice)
        except ValueError:
            print("value error...")
            continue

        if choice == 1:
            create_class(classes)
        elif choice == 2:
            print("\nclasses")
            for c in classes:
                print("-",c)

            class_name = input("select class").title().strip()

            if class_name in classes:
                manage_students(classes[class_name])
            else:
                print("Class Not Found")
        elif choice == 3:
            rename_class(classes)
        elif choice == 4:
            remove_class(classes)
        elif choice == 5:
            generate_group()
        elif choice == 6:
            break