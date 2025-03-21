# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function


import quartzbio
from ..client import client
from .credentials import get_credentials
from .credentials import save_credentials
from .credentials import delete_credentials


def login_and_save_credentials(
    *args,
    api_host: str = None,
    api_key: str = None,
    access_token: str = None,
    name: str = None,
    version: str = None,
):
    """
    CLI command to login and persist credentials to a file
    """

    if args and args[0].access_token:
        access_token = args[0].access_token
    elif args and args[0].api_key:
        api_key = args[0].api_key

    if args and args[0].api_host:
        api_host = args[0].api_host

    quartzbio.login(
        api_host=api_host,
        api_key=api_key,
        access_token=access_token,
        name=name,
        version=version,
    )

    # Print information about the current user
    user = client.whoami()
    print_user(user)

    print("@@@ WHAT??")
    if False:
        save_credentials(
            user["email"].lower(),
            client._auth.token,
            client._auth.token_type,
            quartzbio.api_host,
        )
        print("Updated local credentials file.")
    # else:
    #     print(
    #         "You are not logged-in. Visit "
    #         "https://docs.quartzbio.com/#authentication to get started."
    #     )


def logout(*args):
    """
    Delete's the user's locally-stored credentials.
    """
    if get_credentials():
        delete_credentials()
        print("You have been logged out.")
    else:
        print("You are not logged-in.")


def whoami(*args, **kwargs):
    """
    Prints information about the current user.
    Assumes the user is already logged-in.
    """
    try:
        user = client.whoami()
    except Exception as e:
        print("{} (code: {})".format(e.message, e.status_code))
    else:
        print_user(user)


def print_user(user):
    """
    Prints information about the current user.
    """
    email = user["email"]
    domain = user["account"]["domain"]
    print(
        'You are logged-in to the "{}" domain as {} (server: {}).'.format(
            domain, email, quartzbio.api_host
        )
    )
