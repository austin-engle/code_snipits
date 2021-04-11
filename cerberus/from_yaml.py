from cerberus import Validator
import yaml


state_schema = {
    "type": "dict",
    "schema": {
        "cities": {"type": "list", "schema": {"type": "string"}},
        "capital": {
            "type": "string",
        },
        "stateflower": {"type": "string"},
    },
}


v = Validator()
v.require_all = True
v.schema = {
    "states": {
        "type": "dict",
        "schema": {
            "utah": state_schema,
            "texas": state_schema,
            "illinois": state_schema,
            "missouri": state_schema,
        },
    },
}


with open("cities.yaml") as f:

    data = yaml.load(f, Loader=yaml.FullLoader)
    # print(data)

    if v.validate(data):
        print("valid data")
    else:
        print("invalid data")
        print(v.errors)