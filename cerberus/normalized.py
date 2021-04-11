from cerberus import Validator

v = Validator()

schema = {"amount": {"coerce": int}}
document = {"model": "consumerism", "amount": "1"}

normalized_document = v.normalized(document, schema)

print(type(normalized_document["amount"]))
