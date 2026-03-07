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
    
def set_student_state():
    state = True

    #for student in student_list: #not working yet
     

def main ():
    get_students()
    set_student_state()    
    print(student_list)

main()