name = input("name:")

def is_access(age):
    if age >= 18:
        return True
    else:
        return False

def greet_and_info(name, age):
    if is_access(age):
        return f"Access allowed! \n Hello {name}! Your age is {age}"
    else:
        return f"Access denied!" 

while True:
    age = int(input("age: "))
    if age < 0 or age > 120:
        print("Invalid data. Try again.")
    else:
        break

print(greet_and_info(name, age))

