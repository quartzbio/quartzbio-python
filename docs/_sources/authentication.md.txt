# Authentication

## Pre-Requisites

The EDP supports the use of Python for both Unix (Linux, Mac) and Windows environments. QuartzBio recommends using the latest version of the Python client (v2.12.0 or higher).

After insuring that the user is running an appropriate python version, they can install the EDP Python Library (note: currently named quartzbio) by issuing the following pip call:

```
pip install --upgrade quartzbio
```

After installing the package, users will next create the relevant credential storage files. By default, the EDP Python client uses a stored credentials file located at `~/.quartzbio/credentials`. Credentials are stored in a separate file to avoid having access tokens stored in Python scripts.

To generate the credential storage file, issue the following command in a terminal, replacing the `TOKEN` and `DOMAIN` fields as instructed. to automatically create or update the credentials file:

```Python
# Clear your existing credentials
quartzbio logout

# Replace "TOKEN" with the Personal Access Token copied from the EDP web page
# Replace "DOMAIN" with your account's subdomain (i.e. your company name)
quartzbio login --access-token TOKEN --api-host https://DOMAIN.api.edp.aws.quartz.bio
```
Please note that the API Host variable should not contain a trailing slash, i.e "/" at the end of the URL.



## Python Authentication


Once your credentials are stored, use the `login()` function to automatically load them in a script:

```Python
import quartzbio

# Loads your token from the credentials file
quartzbio.login()
```

Alternatively, you may store your Personal Access Token in the `$QUARTZBIO_ACCESS_TOKEN` environment variable. This will be automatically loaded by the Python client, even if `login()` is not called.



For Python scripts and Dash apps, If you use the credentials file (~/.quartzbio/credentials), modify the line with "machine api.quartzbio.com" to be

```
machine domain.api.quartzbio.com
```
In your scripts, if you use the quartzbio.login() function, modify it to be: 

```
quartzbio.login(api_host="https://domain.api.quartzbio.com")
```
Please once again note that there should be no trailing slash in the host URL.



If you use environment variables for authentication, change `$QUARTZBIO_API_HOST` to https://domain.api.quartzbio.com.



## Testing Credentials



There are a few ways to test credentials. If using the Python client, users can directly run the quartzbio whoami command:

```
$ quartzbio whoami
# You are logged-in to the "***" domain as ****@****.com with role member.
```
A successful authentication will return a statement of the form shown in the commented line.



Users can also directly prompt their username and email within a block of python code as follows:

```
# Login
quartzbio.login()

# Get the current User
user = quartzbio.User.retrieve()
print(user.email)
```