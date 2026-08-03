import requests
from requests.auth import HTTPBasicAuth

class BlazeMeterClient():

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
        response = self.session.get(url)

        if response.status_code == 200:
            print("Successfully authenticated")
            return response.json()

        else:
            print("Authentical Failed")
            print("status:", response.status_code)
            print(response.text)

            return None