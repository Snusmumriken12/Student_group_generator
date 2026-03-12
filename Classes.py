classes = {}

def create_class(classes):
    class_name = input("Enter the name of the class -> ").title().strip()

    if class_name == "":
        print("class name cannot be empty")
        return
    elif class_name in classes:
        print("that class already exist")

    classes[class_name] = []
    print(f"Class '{class_name}' created.")

def rename_class(classes):
   while True:
    choice = input("What Class Name Do You Want To Rename? (Enter to exit)--> ").title().strip()
    if choice == "":
       break
    elif choice in classes:
        new_class_name = input("What Is The New Name? > ").title().strip()

    




def main(classes):
    while True:

        print("\n1. Create Class ")
        print("2. Show classes")
        print("3. rename classes")
        print("3. Exit")

        choice = input("Choose-> ")
        try:
            choice = int(choice)
        except ValueError:    
            print("Value Error...")
        
        if choice == 1:
            create_class(classes)
        
        elif choice == 2:
            print(classes)
        elif choice == 3:
            break
        else:
            print("not a valid number")

main(classes)