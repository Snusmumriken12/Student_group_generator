from storage import load_classes, save_classes
from Classes import create_class, rename_class, remove_class
from students import manage_students

def main():
    classes = load_classes

    while True:
        print("\n1. Create Class")
        print("2. Manage Class Students")
        print("3. Rename Class")
        print("4. Remove Class")
        print("5. Exit")

        choice = input("->")
        try:
            choice = int(choice)
        except ValueError:
            print("value error...")

        if choice == 1:
            create_class(classes)
