def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    result = 0
    for _ in range(y):
        result += x
    return result

def divide(x, y):
    if y == 0:
        raise ValueError("Cannot divide by zero!")
    return x / y

class Calculator:
    def __init__(self):
        self.history = []

    def calculate(self, operation, x, y):
        if operation == "add":
            result = add(x, y)
        elif operation == "subtract":
            result = subtract(x, y)
        elif operation == "multiply":
            result = multiply(x, y)
        elif operation == "divide":
            result = divide(x, y)
        else:
            raise ValueError("Unknown operation")
        
        self.history.append((operation, x, y, result))
        return result

    def show_history(self):
        for entry in self.history:
            print(f"{entry[0]}({entry[1]}, {entry[2]}) = {entry[3]}")
