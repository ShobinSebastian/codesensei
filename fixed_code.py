def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b

def get_item(items, index):
    if index < 0 or index >= len(items):
        raise IndexError("Index out of range")
    return items[index]

try:
    result = divide(10, 0)
except ZeroDivisionError as e:
    print(e)

numbers = [1, 2, 3]
try:
    item = get_item(numbers, 10)
except IndexError as e:
    print(e)