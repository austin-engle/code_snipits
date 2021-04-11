from cerberus import Validator

v = Validator()

v.schema = {
    "name": {"required": True, "type": "string"},
    "sex": {"required": True, "type": "string", "regex": "[MF]"},
}

v.allow_unknown = True

data = {"name": "Austin", "sex": "M", "age": 23}

if v.validate(data):
    print("valid data")
else:
    print("invalid data")
    print(v.errors)

print(v.document)