from storage import load_classes, save_classes
from Classes import create_class, rename_class, remove_class
from student_manage import manage_students
from group_gen import generate_group
from storage import save_groups

def main():
    classes = load_classes()
    class_name, groups = generate_group(classes)

    while True:
        print("\n1. Create Class")
        print("2. Manage Class Students")
        print("3. Rename Class")
        print("4. Remove Class")
        print("5. Generate Group")
        print("6. Show Classes")
        print("7. Exit")

        choice = input("->")
        try:
            choice = int(choice)
        except ValueError:
            print("value error...")
            continue

        if choice == 1:
            create_class(classes)
            save_classes(classes)
        elif choice == 2:
            print("\nclasses")
            for c in classes:
                print("-",c)

            class_name = input("select class").title().strip()

            if class_name in classes:
                manage_students(classes[class_name])
                save_classes(classes)
            else:
                print("Class Not Found")
        elif choice == 3:
            rename_class(classes)
            save_classes(classes)
        elif choice == 4:
            remove_class(classes)
            save_classes(classes)
        elif choice == 5:
            generate_group(classes)
            save_classes(classes)
            save_groups(class_name, groups)
        elif choice == 6:
            print(classes)
        elif choice == 7:
            save_classes(classes)
            break
main()

#bug in the rename student funct: "name does not exist"
#bug in the remove student funct: "student not found"
#bug in the student status funct: "student no found"
#bug classes does not save properly (fixed)
#bug it playes the whole student mange loop when student manage is selected