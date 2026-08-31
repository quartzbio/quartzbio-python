# Creating and Deploying EDP Python Applications

EDP users have the ability to create new apps through the EDP API and Python frameworks such as Dash and Streamlit. EDP applications represent unique OAuth2 credentials that enable a third-party system to obtain EDP access tokens on behalf of EDP users. By default, applications created on the EDP are accessible only to users in the same organization.

The primary advantage of using Python app framework integration with EDP is the ability to authenticate users. This enables developers to create applications that dynamically understand the access permissions of a user in the EDP. For example, a developer can create an application allowing access to other users' vaults without actually having access themselves.

**Note: only `dash` version 1.2.0 and `dash-auth` version 1.3.2 are currently supported.**

## Getting Started

To get started, developers should make sure they have the latest EDP Python module.

```
# Install or update the EDP Python module
pip install --upgrade quartzbio
```

Users should authenticate their Python sessions using their QuartzBio credentials, and can then start using the EDP Python package and their framework of choice to create apps. Each time a user creates a new app, a unique client ID is generated. Users should make sure to save their client IDs to a safe place after creation. Users can always contact EDP Support to retrieve a list of their apps (with their client IDs) in the future.

To create an app, users can enter the following Python commands. Doing so will create the app and allow the user to view its client ID:

```Python
from quartzbio import Application

# Create the app (only once per application)
# using the standard Dash app OAuth2 redirect URL:
my_app = Application.create(
    name='My Dash App',
    redirect_uris='http://127.0.0.1:8050/_oauth-redirect')

# Print the app's client ID
print(my_app.client_id)
```

## Updating Applications

Users can update the redirect URIs of their EDP Python applications as needed, such as when moving from a local development environment to a production environment:

```Python
from quartzbio import Application, User

# Retrieve app (the first that matches the name, owned by the current user)
my_app = Application.all(name='My Dash App', user=User.retrieve().id).next()

# Add the 'write' scope
my_app.scopes = 'read write'

# Add the production redirect URI, but keep the development one
my_app.redirect_uris = """
http://127.0.0.1:8050/_oauth-redirect
https://my-app.my-dash-apps.net/_oauth-redirect
"""

#EDP supports wildcard URIs. If a hosted app has a dynamic value in the URL, such as:
"https://my-app.my-dash-apps.net/notebookSession/123456/_oauth-redirect"
#here `123456` is a session ID that changes for each session, then the redirect URI can be provided as:
"https://my-app.my-dash-apps.net/notebookSession/*/_oauth-redirect"

my_app.save()
```

## Deleting Applications

Users can delete EDP Python applications by issuing the following commands. Deleting the application in this way will revoke the relevant authentication credentials and client ID.

```Python
from quartzbio import Application, User

# Retrieve app (the first that matches the name, owned by the current user)
my_app = Application.all(name='My Dash App', user=User.retrieve().id).next()

# Delete the app
my_app.delete()
```

## Python Dash Applications

Dash is a Python framework for building interactive web apps and dashboards right from Python (no JavaScript required). It is built on top of Plotly.js, React, and Flask, and makes it easy to tie together modern UI elements and complex graphs to analytical Python code. The best way to get comfortable with Dash is to run through their User Guide and Tutorial.

To start, users should install the latest Dash Python module and dependencies:

```
# Install Dash and Dash dependencies
pip install --upgrade dash-html-components dash-renderer dash-core-components dash-auth plotly
```

### Authenticating Users

To integrate EDP into an existing Dash app, users can employ the EDP Dash authentication wrapper. Users should replace their existing app object with one created by the `QuartzBioDash` class instead of the `dash.Dash` class. Users should also make sure to plug in the client ID they received after creating their EDP app.

```Python
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html

# Add the following imports:
from quartzbio.contrib.dash import QuartzBioDash
import flask

# Before: app created with the basic Dash class
# app = dash.Dash()

# After: app created with EDP's Dash class
# Input Client ID
app = QuartzBioDash(
    name=__name__,
    title='My Dash App',
    app_url='http://127.0.0.1:8050',
    client_id='CLIENT ID HERE')

# An example Dash layout:
app.layout = html.Div([
    html.H1('Welcome to your Dash app!'),
    html.Div(id='quartzbio-auth')
])


@app.callback(
    dash.dependencies.Output('quartzbio-auth', 'children'),
    [dash.dependencies.Input('quartzbio-auth', 'value')])
def quartzbio_auth(pathname):
    """Show current user on first page load."""
    user = flask.g.client.User.retrieve()
    return [
        html.P('Logged-in as: {}'.format(user.full_name)),
        html.A('Log out', href='/_dash-logout')
    ]


if __name__ == '__main__':
    app.run_server(debug=True)
```

In callback functions, users can use the `flask.g.client` shortcut to access the EDP session for the currently logged-in user.

To run the app, users can open their shells and run the following command:

```
python app.py
```

Now, they can open http://127.0.0.1:8050 in their web browsers to access the app.

### Deploying Dash Apps

For deploying Dash apps, users may use a third-party service such as Heroku, Amazon Web Services, or Google Cloud Platform to deploy their app. Users should keep in mind that their data may be accessible by a third-party system if they choose one of these options.

#### Deploy to Heroku

The example EDP Dash app for Heroku uses the EDP API to pull data. Users can also run the app locally using an EDP OAuth2 client ID or a personal EDP access token.

Users will need to set the following environment variables to deploy the app to Heroku:

- `SECRET_KEY`: A secret key generated specifically for the app.
- `CLIENT_ID`: The EDP app's client ID.
- `APP_URL`: The public URL of the app (e.g. `https://<APP NAME>.herokuapp.com`).

Users who want to deploy manually with the Heroku CLI should first create a new Heroku app:

```
# Create the Heroku app
heroku create

# Set the SECRET_KEY to random characters
heroku config:set SECRET_KEY=somesecretkey123

# Set EDP OAuth2 client ID
heroku config:set CLIENT_ID=<client id>

# Set app's public URL
heroku config:set APP_URL=https://<app name>.herokuapp.com

git push heroku master
```

Users can run the following one-liner from their command lines to generate a secret key:

```
python -c "import binascii, os; print(binascii.hexlify(os.urandom(24)))"
```

## Python Streamlit Applications

Streamlit is an open-source Python framework for Machine Learning and Data Science teams. It allows users to create interactive web apps and dashboards all in pure Python. In just a few minutes users can build powerful data apps in a couple of lines of code. Streamlit dashboard examples can be found in the Streamlit Gallery. The best way to get comfortable with the Streamlit framework is to run through their Get started section, and the full list of Streamlit building blocks can be found in the API reference section.

### Authenticating Users

To integrate EDP into an existing Streamlit app, users can employ the EDP Streamlit authentication wrapper. First, users should ensure they have the latest Streamlit Python module:

```
# Install Streamlit
pip install --upgrade streamlit

# Test that the installation worked
streamlit hello
```

The user should then copy their app's client ID and secret to the app's `.env` file, as well as the redirect URI:

```
CLIENT_ID=APP_ID
CLIENT_SECRET=APP_SECRET

REDIRECT_URI=http://localhost:8501
```

Once the user has successfully authenticated the EDP Python session, the OAuth2 token and the initialized EDP client are saved to the Streamlit session state. Users can access them with the following commands:

```Python
import streamlit as st

st.session_state.quartzbio_client
st.session_state.token
```

The `QuartzBioStreamlit` class is used to wrap Streamlit apps with EDP OAuth2:

```Python
import streamlit as st
import pandas as pd

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from quartzbio.contrib.streamlit.solvebio_streamlit import QuartzBioStreamlit


@st.cache
def get_personal_vault_items(vault):
    """Get items from the personal vault (cached using the Streamlit cache mechanism)"""

    files = vault.files()
    folders = vault.folders()
    datasets = vault.datasets()

    return files, folders, datasets


def streamlit_demo_app():
    """Streamlit demo app

    It fetches the EDP client (initialised with an OAuth2 token) from the
    Streamlit session state and makes API calls through that client.
    """

    # Getting the EDP client from the Streamlit session state
    quartzbio_client = st.session_state.quartzbio_client

    st.title("EDP App")

    # EDP user
    user = quartzbio_client.User.retrieve()
    st.header("{}'s personal vault overview:".format(user["first_name"]))

    # Personal vault
    vault = quartzbio_client.Vault.get_personal_vault()
    st.write(vault["description"])

    files, folders, datasets = get_personal_vault_items(vault)

    # Visualizing the stats from the personal vault
    data = {
        "Number of files": [files["total"]],
        "Number of datasets": [datasets["total"]],
        "Number of folders": [folders["total"]],
    }
    chart_data = pd.DataFrame.from_dict(
        data, columns=["Number of items"], orient="index"
    )
    st.write(chart_data)
    st.bar_chart(chart_data)

    # Listing items from the personal vault
    st.subheader("List selected items")
    option = st.radio("Select EDP platform:", ("Files", "Folders", "Datasets"))
    if option == "Files":
        for item in files:
            st.markdown("- {}".format(item["filename"]))
    elif option == "Folders":
        for item in folders:
            st.markdown("- {}".format(item["filename"]))
    elif option == "Datasets":
        for item in datasets:
            st.markdown("- {}".format(item["filename"]))


# Wrapping the Streamlit app with EDP OAuth2
secure_app = QuartzBioStreamlit()
secure_app.wrap(streamlit_app=streamlit_demo_app)
```

To run the app, users can open their shells and enter the following command:

```
streamlit run app.py
```

Now, they can open http://127.0.0.1:8501 in their web browsers to access the app.

### Deploying Streamlit Apps

For deploying Streamlit apps, users may use the Streamlit Cloud. They may also use a third-party service such as Heroku, Amazon Web Services, or Google Cloud Platform to deploy their app. Users should keep in mind that their data may be accessible by a third-party system if they choose one of these options.

## Other Web Frameworks

EDP users interested in application development are currently recommended to use Shiny for R and Dash for Python. Users who are interested in using other web frameworks such as Django, Rails, React, or others may contact EDP Support.

There are many ways to deploy applications and a user's organization may have a preferred deployment strategy. Users are recommended to reach out to their IT department to help select the best strategy for deploying apps to a production environment. In some cases, QuartzBio can deploy and manage client apps within the QuartzBio infrastructure. Users can contact EDP Support for more information.

## Applications Endpoints

This API reference is organized by resource type and endpoint. Each resource type has one or more data representations and one or more methods. Methods do not accept URL parameters or request bodies unless specified.

**Note: if your EDP endpoint is `sponsor.edp.aws.quartz.bio`, you would use `sponsor.api.edp.aws.quartz.bio`.**

All the endpoints below share the same base URL:

```
BASE = https://<EDP_API_HOST>/v2
```

| Method | HTTP Request | Description | Authorization | Response |
|---|---|---|---|---|
| create | `POST {BASE}/applications` | Create an application. | This request requires an authorized user with permission to create new applications. | The response contains a single Application resource. |
| delete | `DELETE {BASE}/applications/{CLIENT_ID}` | Delete an application. | This request requires an authorized user with permission to modify the target application. | The response returns "HTTP 200 OK" when successful. |
| get | `GET {BASE}/applications/{CLIENT_ID}` | Retrieve metadata about an application. | This request requires an authorized user with permission to view the target application. | The response contains an Application resource. |
| secret | `GET {BASE}/applications/{CLIENT_ID}/secret` | Retrieve an application's secret key. | This request requires an authorized user with permission to view the target application's secret key. | The response contains an Application resource with an additional `client_secret` attribute. |

The `create` request accepts the following properties:

| Property | Value | Description |
|---|---|---|
| name | string | (required) A user-visible name for the app. |
| redirect_uris | string | (required) A list of space-separated valid redirection endpoint URIs. Endpoints can use regex format, like `https://my-app.my-dash-apps.net/notebookSession/*/_oauth-redirect` |
| description | string | A user-friendly description of the app. |
| help_url | string | The URL where documentation about the app can be found. |
| scopes | string | OAuth2 scopes required to use the app (`read` or `read write`). |
| source_url | string | The URL where the app's source code can be found. |
| tags | string (list) | A list of arbitrary tags to categorize the app. |
| web_url | string | The URL where the app can be accessed by users. |
