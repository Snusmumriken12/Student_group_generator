def get_students(student_list):
    seen_names = {student["name"] for student in student_list}

    print("Type a student's name")
    print("When you are done just press enter")

    while True:
        name = input("Student name: ").strip().lower().title()

        if name == "":
            break

        if name in seen_names:
            warning = input(f"{name} already exists, add anyway? y/n -> ").strip().lower()
            if warning == "n":
                continue

        seen_names.add(name)

        student_list.append({
            "name": name,
            "status": True
        })

    return seen_names


def set_student_state(student_list, seen_names):
    print("Is there any student that is not present?")
    print("Press enter to continue")

    for student in student_list:
        if student["status"]:
            print(f"{student['name']} (PRESENT)")
        else:
            print(f"{student['name']} (ABSENT)")

    while True:
        status = input("-> ").strip().lower().title()

        if status == "":
            break

        if status in seen_names:
            for student in student_list:
                if student["name"] == status:
                    student["status"] = not student["status"]
                    break
        else:
            print("Name does not exist...")


def remove_student(student_list, seen_names):
    print("Do you want to remove a student from the class?")
    print("Press enter to continue")

    for student in student_list:
        print(student["name"])

    while True:
        rem_student = input("Student name -> ").strip().lower().title()

        if rem_student == "":
            break

        if rem_student in seen_names:
            for student in student_list:
                if student["name"] == rem_student:
                    student_list.remove(student)
                    seen_names.remove(rem_student)
                    break
        else:
            print("Student not found...")


def rename_student(student_list, seen_names):
    while True:
        change_student = input("What student do you want to rename? (enter to exit) -> ").strip().lower().title()

        if change_student == "":
            break

        if change_student in seen_names:
            new_name = input("What should the new name be? ").strip().lower().title()

            if new_name == "":
                print("Name can't be empty")
                continue

            if new_name in seen_names:
                print("That name already exists")
                continue

            for student in student_list:
                if student["name"] == change_student:
                    student["name"] = new_name
                    seen_names.remove(change_student)
                    seen_names.add(new_name)
                    break
        else:
            print("Student not found...")


def manage_students(student_list):
    while True:
        seen_names = {student["name"] for student in student_list}

        print("\n1. add students")
        print("2. mark students present/absent")
        print("3. remove student from class")
        print("4. rename a student")
        print("5. Show students")
        print("6. back")
        choice = input("--> ")
        if choice == "":
            print("cant be empty")
            continue
        try:
            choice = int(choice)
        except ValueError:
            print("ValueError")
            continue

        if choice == 1:
            get_students(student_list)
        elif choice == 2:
            set_student_state(student_list, seen_names)
        elif choice == 3:
            remove_student(student_list, seen_names)
        elif choice == 4:
            rename_student(student_list, seen_names)
        elif choice == 5:
            for student in student_list:
                print(student["name"])
        elif choice == 6:
            break



    #get_students(student_list)
    #seen_names = {student["name"] for student in student_list}

    #set_student_state(student_list, seen_names)
    #remove_student(student_list, seen_names)
    #rename_student(student_list, seen_names)

