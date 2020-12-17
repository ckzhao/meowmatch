import urllib.request, urllib.error, urllib.parse, json, webbrowser
from flask import Flask, render_template, request
import http.client


def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)


def safe_get(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print("The server couldn't fulfill the request.")
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
        headers={},  # The headers you want
    )
    result = safe_get(req)
    if result is not None:
        return json.load(result)


result = geturl("https://api.petfinder.com/v2/oauth2/token")
token = result['access_token']

def getresult(token, params):
    result = urllib.parse.urlencode({'type': 'cat', 'limit': '20'})
    genders = []
    ages = []
    location = []
    distance = []
    good_with_children = []
    good_with_cats = []
    good_with_dogs = []
    for i in params:
        if i == "location":
            location.append(params[i])
        if i == "distance":
            distance.append(params[i])
        if i == "surprise_me":
            genders.append('female')
            genders.append('male')
            ages.append('baby')
            ages.append('young')
            ages.append('adult')
            ages.append('senior')
        else:
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
            if i == "good_with_children":
                good_with_children.append('true')
            if i == "good_with_cats":
                good_with_cats.append('true')
            if i == "good_with_dogs":
                good_with_dogs.append('true')

    if len(genders) > 0:
        data_string = "&gender=" + ",".join(genders)
    if len(ages) > 0:
        data_string += "&age=" + ",".join(ages)
    if len(good_with_children) > 0:
        data_string += "&good_with_children=" + ",".join(good_with_children)
    if len(good_with_cats) > 0:
        data_string += "&good_with_cats=" + ",".join(good_with_cats)
    if len(good_with_dogs) > 0:
        data_string += "&good_with_dogs=" + ",".join(good_with_dogs)
    if len(location) > 0:
        data_string += "&location=" + ",".join(location)
    if len(distance) > 0:
        data_string += "&distance=" + ",".join(distance)

    req = urllib.request.Request(
        url="https://api.petfinder.com/v2/animals?" + result + data_string,  # The url you wanna get
        headers={"Authorization": "Bearer " + token},  # The headers you want
    )
    data_result = safe_get(req)
    if data_result is not None:
        return json.load(data_result)


@app.route("/gresponse")
def greet_response_handler():
    output = getresult(token, request.args)
    count = 0
    names = {}
    results_dict = {}
    for i in output["animals"]:
        count += 1
        results_dict[count] = {}
        if i["primary_photo_cropped"] != None:
            results_dict[count]["photos"] = i["primary_photo_cropped"]["full"]
        else:
            results_dict[count]["photos"] = "http://www.newdesignfile.com/postpic/2015/02/no-icon-available_68024.png"
        results_dict[count]["name"] = str(i["name"].strip())
        results_dict[count]["name"] = results_dict[count]["name"].replace("&", "")
        results_dict[count]["name"] = results_dict[count]["name"].replace(" ", "")
        results_dict[count]["name"] = results_dict[count]["name"].replace(",", "")
        names[count] = i["name"]
        results_dict[count]["gender"] = i["gender"]
        results_dict[count]["age"] = i["age"]
        results_dict[count]["description"] = i["description"]
        results_dict[count]["url"] = i["url"]
        results_dict[count]["distance"] = str(i["contact"]["address"]["city"]) + " (" + str(i["distance"]) + " mi away)"

    return render_template("match.html", results_dict=results_dict, love_data=getlove(request.args, names))

def getlove(params, names):
    username = str(params["username"])
    love_data = {}
    for name in names:
        current_name = str(names[name].strip())
        current_name = current_name.replace("&", "")
        current_name = current_name.replace(" ", "")
        current_name = current_name.replace(",", "")
        conn = http.client.HTTPSConnection("love-calculator.p.rapidapi.com")
        headers = {
            "x-rapidapi-key": "c1858c8c2emsh6cecb4e9b7f8a5fp10d437jsn3b4fe1fab958",
	        "x-rapidapi-host": "love-calculator.p.rapidapi.com"}
        conn.request("GET", "/getPercentage?fname=" + str(username) + "&sname=" + current_name, headers=headers)
        loveresult = conn.getresponse()
        data = loveresult.read()
        lovestr = data.decode("utf-8")
        lovedict = json.loads(lovestr)
        love_data[current_name] = {}
        love_data[current_name]["percentage"] = "Love Calculation: " + str(lovedict["percentage"]) + "%"
        love_data[current_name]["result"] = lovedict["result"]
    return love_data


@app.route('/')
def meow():
    return render_template("website.html")


if __name__ == "__main__":
    # Used when running locally only.
    # When deploying to Google AppEngine, a webserver process
    # will serve your app.
    app.run(host="localhost", port=8081, debug=True)
