from cerberus import Validator

v = Validator()
v.schema = {
    "name": {'required': True, "type": "string", "minlength": 2},
    "age": {"type": "integer", "min": 18, "max": 65},
}

if v.validate({"name": "Jd", "age": 18}):
    print("valid data")
else:
    print("invalid data")
    print(v.errors)