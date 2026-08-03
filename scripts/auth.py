import requests
import logging
from requests.auth import HTTPBasicAuth

class BlazeMeterClient:

    def __init__(self, config):
        
        self.base_url = config["blazemeter"]["base_url"]
        self.api_key = config["blazemeter"]["api_key"]
        self.api_secret = config["blazemeter"]["api_secret"]

        # Create HTTP session first
        self.session = requests.Session()


        self.session.auth = HTTPBasicAuth(
            self.api_key,
            self.api_secret
        )

        self.session.headers.update({
            "Content-Type": "application/json"
        })

    def test_connection(self):
        url = f"{self.base_url}/api/v4/user"
        try:
            response = self.session.get(url,timeout=30)

            if response.status_code == 200:
                # print("Successfully authenticated") # this if for running local
                logging.info("Successfully Authenticated") # used this to run for jenkins logging
                return response.json()

            logging.error(f"Authentication Failed. Status: {response.status_code}")
            logging.error(response.text)
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Connection Error: {e}")
            return None