import os

for file_name in os.listdir("Test_data"):
    os.rename(os.path.join("Test_data", file_name), os.path.join("C:/Work/Input", file_name))
    os.copy_file_range()

for i in (1, 2, 3):
    print(i)