students = []
name = None

num_student = input("how many students will you add? >")
num_student = int(num_student)
print("type a students name")
print("when you are done just press enter")
for i in num_student:
    name = input("student name: ").lower().title

    if name == "":
        continue
    students.append({
        "name": name
    })
    

print(students)