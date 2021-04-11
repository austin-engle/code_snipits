from cerberus import Validator

v = Validator()
v.schema = {
    "name": {"required": True, "type": "string", "minlength": 2},
    "age": {"type": "integer", "min": 18, "max": 65},
}

if v.validate({"name": "Austin", "age": 23}):
    print("valid data")
    print(v.document)
else:
    print("invalid data")
    print(v.errors)