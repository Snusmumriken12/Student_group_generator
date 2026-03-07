student_list = []

def get_students():
    seen_names = set()
    print("type a students name")
    print("when you are done just press enter")
    while True:
        name = input("student name: ").strip()
        name = name.lower().title()

        if name == "":
            break
        if name in seen_names:
            warning = input(f"{name} already exist are you sure you want to add it? y/n").strip().lower()
            if warning == "n":
                continue
        seen_names.add(name)

        student_list.append({
            "name": name
        })

get_students()

print(student_list)