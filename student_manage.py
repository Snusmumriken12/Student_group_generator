import json
from storage import save_students, load_students
student_list = []
def get_students():
    seen_names = set()
    seen_names = {student["name"] for student in student_list}
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
            "status": True
        })

    return seen_names
def set_student_state(seen_names):
    print("is there any students that are not present?")
    print("enter to continue")
    for student in student_list:
        if student["status"]:
            print(f"{student['name']} (PRESENT)")
        else:
            print(f"{student['name']} (ABSENT)")
    

    while True:
        status = input("-> ").strip()
        status = status.lower().title()
        if status == "":
            break
        elif status in seen_names:    
           for student in student_list:
               if student["name"] == status:
                    student["status"] = not student["status"]
                    break
        
        else:
            print("name does not exist...")

def remove_student(seen_names):
    print("Do you want to remove a student from the group?")
    print("just press enter to contiune: ")
    for student in student_list:
        print(student["name"])

    while True:
        rem_student = input("student name--> ").strip()
        rem_student = rem_student.lower().title()
        if rem_student == "":
            break

        elif rem_student in seen_names:
            for student in student_list:
                if student["name"] == rem_student:
                    student_list.remove(student)
                    seen_names.remove(rem_student)
        
        else:
            print("Student not found...")

def rename_student(seen_names):
    while True:
        change_student = input("What student do you want to rename? (enter to exit) --> ").strip()
        change_student = change_student.lower().title()
        if change_student == "":
            break
        elif change_student in seen_names:
            new_name = input("what should the new name be?").strip()
            new_name = new_name.lower().title()
            for student in student_list:
                if student["name"] == change_student:
                    student["name"] = new_name
                    seen_names.remove(change_student)
                    seen_names.add(new_name)
        else:
            print("student not found...")  
             
def manage_students(student_list):

    seen_names = {student["name"] for student in student_list}

    get_students()
    set_student_state(seen_names)
    remove_student(seen_names)
    rename_student(seen_names) 

def main ():
    global student_list
    student_list = load_students()
    seen_names = get_students()
    set_student_state(seen_names)    
    remove_student(seen_names)
    rename_student(seen_names)
    for student in student_list:
        if student["status"] == True:
            print (student["name"])
        else:
            print(f"{student['name']} (ABSENT)")
    save_students(student_list)


main()