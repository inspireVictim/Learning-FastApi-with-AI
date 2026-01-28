users = []

def is_valid_age(age):
    return 0<= age <= 120

def is_access(age):
    return age >= 18

def save_user(name, age):
    users.append({
        "name": name,
        "age" : age,
        "access" : is_access(age)
        })

def greet_and_info(name, age):
    save_user(name, age)
    if is_access(age):
        return f"Hello, {name}! Your age is {age}"
    else:
        return f"Access denied!"

name = input("name: ")

while True:
    age = int(input("age: "))
    if not is_valid_age(age):
        print("Invalid data, try again!")
    else:
        break

print(greet_and_info(name, age))
print("users:", users)
