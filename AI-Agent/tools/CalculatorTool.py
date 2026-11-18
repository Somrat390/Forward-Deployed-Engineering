import math

def calculate(operation, a, b):
    print("Calculator tool called")

    if operation == "add":
        return a + b
    if operation == "subtract":
        return a - b
    if operation == "multiply":
        return a * b
    if operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by 0")
        return a / b
    if operation == "mod":
        if b == 0:
            raise ValueError("Cannot calculate mod by 0")
        return a % b
    if operation == "power":
        return math.pow(a, b)
    raise ValueError(f"Unsupported operation {operation}")