classes = {
    "4a": [],
    "5a": []
}

def create_class(classes):
    class_name = input("Enter the name of the class -> ")

    if class_name == "":
        print("class name cannot be empty")
        return
    elif class_name in classes:
        print("that class already exist")

    classes[class_name] = []
    print(f"Class '{class_name}' created.")