import json

def read():
    with open('path_to_file/person.json') as f:
        data = json.load(f)

# Output: {'name': 'Bob', 'languages': ['English', 'Fench']}