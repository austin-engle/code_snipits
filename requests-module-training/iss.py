import requests
import json
from datetime import datetime

# 200: Everything went okay, and the result has been returned (if any).
# 301: The server is redirecting you to a different endpoint. This can happen when a company switches domain names, or an endpoint name is changed.
# 400: The server thinks you made a bad request. This can happen when you don’t send along the right data, among other things.
# 401: The server thinks you’re not authenticated. Many APIs require login credentials, so this happens when you don’t send the right credentials to access an API.
# 403: The resource you’re trying to access is forbidden: you don’t have the right permissions to see it.
# 404: The resource you tried to access wasn’t found on the server.
# 503: The server is not ready to handle the request.


# Invalid endpoint that will return a 404
response = requests.get("http://api.open-notify.org/this-api-doesnt-exist")
print(response.status_code)

# Proper API that will return 200 code
response = requests.get("http://api.open-notify.org/astros.json")
print(response.status_code)


# turn response into json object that can be parsed
# Writing to astros.json for easier visibility
with open("astros.json", "w") as file:
    file.write(json.dumps(response.json()))

# loop through and grab names of astros onboard
json_obj = response.json()

people = []

for astro in json_obj["people"]:
    people.append(astro["name"])

with open("astros_names.text", "w") as file:
    file.write(str(people))


# API That takes parameters
parameters = {"lat": 40.71, "lon": -74}

response = requests.get("http://api.open-notify.org/iss-pass.json", params=parameters)

json_response = response.json()

# turn response into json object that can be parsed
# Writing to iss-pass.json for easier visibility
with open("iss-pass.json", "w") as file:
    file.write(json.dumps(json_response))

risetimes = []

for time in json_response["response"]:
    risetimes.append(time["risetime"])


# grab all risetime from response object and add them to the file

with open("iss_times.text", "w") as file:
    for rt in risetimes:
        time = datetime.fromtimestamp(rt)
        file.write(f"{str(time)}\n")