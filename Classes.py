classes = {}

def create_class(classes):
    class_name = input("Enter the name of the class -> ")

    if class_name == "":
        print("class name cannot be empty")
        return
    elif class_name in classes:
        print("that class already exist")

    classes[class_name] = []
    print(f"Class '{class_name}' created.")

while True:

    print("\n1. Create Class ")
    print("2. Show classes")
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

create_class(classes)