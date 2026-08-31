# Developing EDP Applications with Flask

EDP users have the ability to create new apps through the EDP API and Python frameworks such as Flask. EDP applications represent unique OAuth2 credentials that enable a third-party system to obtain EDP access tokens on behalf of EDP users. By default, applications created on the EDP are accessible only to users in the same organization.

## Creating Apps

To get started, users can create a personal access token on the EDP web interface and access the EDP Python client library. Each time users create a new app, they will be granted a unique client ID and client secret:

```Python
from quartzbio import Application
from quartzbio.client import client

#EDP supports wildcard URIs. If a hosted app has a dynamic value in the URL, such as:
"https://my-app.my-dash-apps.net/notebookSession/123456/_oauth-redirect"
#here `123456` is a session ID that changes for each session, then the redirect URI can be provided as:
"https://my-app.my-dash-apps.net/notebookSession/*/_oauth-redirect"

# Create the app (only do this once per application)
# Using an example Flask app OAuth2 redirect URL:
my_app = Application.create(
    name='My Flask App',
    redirect_uris='http://127.0.0.1:5000/callback')

# Print the app's client ID
print(my_app.client_id)

# Print the app's client secret
secret = client.get("/v2/applications/{APP-CLIENT-ID}/secret", {})['client_secret']
print(secret)
```

The client ID and client secret are a critical part of the OAuth2 Authorization Code flow, so users should make sure to copy them to a safe place. Users can always contact QuartzBio Support to retrieve client IDs and secrets.

## Application Example

Below is an example of EDP integration with Flask. For more information about updating and deleting EDP applications as well as other application frameworks, users can refer to the Python Applications documentation.

**Note: if your EDP endpoint is `sponsor.edp.aws.quartz.bio`, you would use `sponsor.api.edp.aws.quartz.bio`.**

```Python
import requests
import os

from flask import Flask, redirect, request, session
import quartzbio

app = Flask(__name__)
app.secret_key = "your_flask_secret_key"

# Replace these values with your QuartzBio EDP client_id and client_secret
# You may also request a client ID and secret from our support team
CLIENT_ID = os.environ.get("{CLIENT_ID}")
CLIENT_SECRET = os.environ.get("{CLIENT_SECRET}")

# Set this to the web-app you would like to connect to
DOMAIN = "{DOMAIN}"

# Set this to your local redirect URI (OAuth2 redirect)
# this must also be set in the application configured in the EDP
REDIRECT_URI = "http://127.0.0.1:5000/callback"

# Do not change these parameters
API_HOST = f"https://{DOMAIN}.api.edp.aws.quartz.bio"
WEB_HOST = f"https://{DOMAIN}.edp.aws.quartz.bio"
AUTH_URL = f"{WEB_HOST}/authorize"
TOKEN_URL = f"{API_HOST}/v1/oauth2/token"


@app.route("/")
def index():
    # Redirect user to QuartzBio's OAuth2 endpoint
    if session.get("access_token"):
        client = quartzbio.QuartzBioClient(
            host=API_HOST, token=session["access_token"], token_type="Bearer"
        )

        # Return HTML with current user
        user = client.User.retrieve()
        print(user)
        return f"Logged-in as: {user.full_name}", 200
    else:
        auth_endpoint = f"{AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
        return redirect(auth_endpoint)


@app.route("/callback")
def callback():
    # Get the authorization code from the API redirect
    code = request.args.get("code")

    # Exchange the code for an access token
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(TOKEN_URL, data=token_data)
    data = response.json()

    if "access_token" in data:
        session["access_token"] = data["access_token"]

        # Now you can use this token to make API requests to the EDP
        print("Authenticated successfully!")
        return redirect("/")
    else:
        return "Authentication failed!", 400


if __name__ == "__main__":
    app.run(debug=True)
```
