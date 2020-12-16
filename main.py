import urllib.request, urllib.error, urllib.parse, json, webbrowser
from flask import Flask, render_template, request

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def safe_get(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print("The server couldn't fulfill the request." )
        print("Error code: ", e.code)
    except urllib.error.URLError as e:
        print("We failed to reach a server")
        print("Reason: ", e.reason)
    return None

api_key = "NlwZwFAhinS7SHc4olp0vFjFDGsu0a9zynrZfVbkH8zqKJVBCK"
api_secret = "YLhRCtT8aTEWihpc6Y9iBGZTrw76dxUhJayh302o"
url = 'https://api.petfinder.com/v2/oauth2/token'
app = Flask(__name__)

def geturl(url):
    data = {
        "grant_type": "client_credentials",
        "client_id": "NlwZwFAhinS7SHc4olp0vFjFDGsu0a9zynrZfVbkH8zqKJVBCK",
        "client_secret": "YLhRCtT8aTEWihpc6Y9iBGZTrw76dxUhJayh302o"
    }
    req = urllib.request.Request(
        url=url,  # The url you wanna get
        data=urllib.parse.urlencode(data).encode('ascii'),
        headers={}, # The headers you want
    )
    result = safe_get(req)
    if result is not None:
        return json.load(result)

result = geturl("https://api.petfinder.com/v2/oauth2/token")
token = result['access_token']

params={}

def getresult(token, params):
    result = urllib.parse.urlencode({'type': 'cat', 'limit': 10})
    data = {}
    genders = []
    ages = []
    for i in params:
        if i == "gender_female":
            genders.append('female')
        elif i == "gender_male":
            genders.append('male')
        if i == "age_baby":
            ages.append('baby')
        elif i == "age_young":
            ages.append('young')
        elif i == "age_adult":
            ages.append('adult')
        elif i == "age_senior":
            ages.append('senior')


        # result = result + "&" + i + ":" + data[i]


    if len(genders) > 0:
        data_string = "gender=" + ",".join(genders)
    if len(ages) > 0:
        data_string += "&age=" + ",".join(ages)
    print(data_string)


    req = urllib.request.Request(
        url="https://api.petfinder.com/v2/animals?" + data_string,  # The url you wanna get
        headers={"Authorization": "Bearer " + token}, # The headers you want
    )
    result = safe_get(req)
    if result is not None:
        return json.load(result)


@app.route("/gresponse")
def greet_response_handler():
    print(getresult(token, request.args))
    return "poopoo juju"

@app.route('/meow_matches')
def meow():
    return "meow"

@app.route('/')
def woof():
    return render_template("website.html")

if __name__ == "__main__":
    # Used when running locally only.
    # When deploying to Google AppEngine, a webserver process
    # will serve your app.
    app.run(host="localhost", port=8081, debug=True)