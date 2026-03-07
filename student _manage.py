student_list = []
def get_students():
    seen_names = set()
    state = True
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
            "name": name,
            "status": state
        })
    return name
def set_student_state(name):
    print("is there any students that are not present?")
    print(student_list)
    status = input("-> ")




def main ():
    get_students()
    #set_student_state()    
    print(student_list)

main()