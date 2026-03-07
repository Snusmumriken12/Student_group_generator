student_list = []

def get_students():
    print("type a students name")
    print("when you are done just press enter")
    while True:
        name = input("student name: ").strip()
        name = name.lower().title()

        if name == False:
            break
        student_list.append({
            "name": name
        })
        

    print(student_list)