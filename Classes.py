classes = {}

def create_class(classes):
    class_name = input("Enter the name of the class -> ").title().strip()

    if class_name == "":
        print("class name cannot be empty")
        return
    elif class_name in classes:
        print("that class already exist")
        return
    classes[class_name] = []
    print(f"Class '{class_name}' created.")

def rename_class(classes):
   print("\n Existing Classes")
   for c in classes:
       print("-", c)
   while True:
    choice = input("What Class Name Do You Want To Rename? (Enter to exit)--> ").title().strip()
    if choice == "":
       break
    elif choice in classes:
        new_class_name = input("What Is The New Name? > ").title().strip()
        if new_class_name == "":
            print("class name cant be empty")
        elif new_class_name in classes:
            print("class name already exist")
        else:
            classes[new_class_name] = classes[choice]
            del classes[choice]
            print(f"{choice} renamed to {new_class_name}")
            break

    else:
        print("class not found")

def remove_class(classes):
    print("\n Existing Classes")
    for c in classes:
        print("-", c)
    while True:
        choice = input("What Class Do You Want To Remove? (enter to exit) -> ").title().strip()

        if choice == "":
            break
        elif choice in classes:
            print (f"Are You Sure You Want To Delete {choice}?")
            confirm = input("y/n").lower()
            if confirm == "y":
                del classes[choice]
                break
            else:
                print("deletion cancelled")
        else:
            print("class not found...")
    





