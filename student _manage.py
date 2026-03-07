student_list = []

def get_students():
    print("type a students name")
    print("when you are done just press enter")
    while True:
        name = input("student name: ").strip()
        name = name.lower().title()

        if name == "":
            break
        student_list.append({
            "name": name
        })

get_students()

print(student_list)