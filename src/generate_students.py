import pandas as pd

students = []

for i in range(1,41):

    reg = f"23MIS{i:04d}"

    name = f"Student{i}"

    students.append([reg,name])

df = pd.DataFrame(students, columns=["ID","Name"])

df.to_csv("students.csv", index=False)

print("students.csv created")