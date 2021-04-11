from cerberus import Validator

v = Validator()
v.require_all = True
v.schema = {
    "name": {"required": True, "type": "string"},
    "age": {"type": "integer"},
    "gender": {"type": "string"},
}

data = {"name": "Austin", "age": 23, "gender": "male"}
if v.validate(data):
    print("valid data")
    print(v.document)
else:
    print("invalid data")
    print(v.errors)
