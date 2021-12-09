#!/usr/bin/env python3

import sys
import json
from datetime import datetime, timedelta

import requests
import singer
from singer import metadata
from odata import ODataService

from tap_dynamics.discover import discover
from tap_dynamics.sync import sync

LOGGER = singer.get_logger()

REQUIRED_CONFIG_KEYS = [
    "start_date",
    "client_id",
    "client_secret",
    "tenant_id",
    "base_url",
    "api_url",
]


def do_discover(service):
    LOGGER.info("Testing authentication")
    try:
        pass  ## TODO: test authentication
    except:
        raise Exception("Error testing Dynamics authentication")

    LOGGER.info("Starting discover")
    catalog = discover(service)
    return catalog


class AuthError(Exception):
    pass


class DynamicsAuth(requests.auth.AuthBase):
    def __init__(self, config):
        self.__client_id = config["client_id"]
        self.__client_secret = config["client_secret"]
        self.__tenant_id = config["tenant_id"]
        self.__api_url = config["api_url"]
        self.__base_url = config["base_url"]

        self.__scope = f'{self.__base_url}.default'
        self.__session = requests.Session()
        self.__access_token = None

    def ensure_access_token(self):
        if self.__access_token is None:
            url = (
                f"https://login.microsoftonline.com/{self.__tenant_id}/"
                f"oauth2/v2.0/token"
            )
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {
                "client_id": self.__client_id,
                "scope": self.__scope,
                "client_secret": self.__client_secret,
                "grant_type": "client_credentials"
            }

            raw_response = requests.post(url, headers=headers, data=data)
            response = self.parse_response(raw_response)
            self.__access_token = response["access_token"]

    def parse_response(self, response):
        if response.status_code != 200:
            raise AuthError(
                f"URL {response.url} retrieved status {response.status_code}."
                f"\nRaw message: {response.text}"
            )
        return response.json()

    def __call__(self, r):
        self.ensure_access_token()
        r.headers["Authorization"] = "Bearer {}".format(self.__access_token)
        return r


@singer.utils.handle_top_exception(LOGGER)
def main():
    parsed_args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)

    url = parsed_args.config["api_url"]

    service = ODataService(
        url, reflect_entities=True, auth=DynamicsAuth(parsed_args.config)
    )
    catalog = parsed_args.catalog or do_discover(service)
    if parsed_args.discover:
        json.dump(catalog.to_dict(), sys.stdout, indent=2)

    else:
        sync(
            service,
            catalog,
            parsed_args.state,
            parsed_args.config["start_date"],
        )


if __name__ == "__main__":
    main()
