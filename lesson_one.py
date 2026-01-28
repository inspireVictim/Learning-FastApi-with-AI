name = str(input("name:"))
age = int(input("AGE:"))

def greet_info(name ,age):
    if age >= 18:
        return f"Hello {name}! Your age is {age}"
    else:
        return "access denied"

#print(greet_info(name, age))

def is_access_allowed(age):
    if age >= 18:
        return True
    else:
        return False

def checked_and_info(name, age):
    if is_access_allowed(age):
        return f"Access allowed! \n Hello {name}! Your age is {age}"
    else:
        return f"Access denied"

print(checked_and_info(name, age))

