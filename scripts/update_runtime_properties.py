"""

transactionRate
environment
branch
clientCode
broker
thinkTime
etc.

"""

"""
Update JMeter properties for BlazeMeter Performance Test

API:

PUT /api/v4/tests/{test_id}

"""


import json
import yaml
import logging


logger = logging.getLogger(__name__)


class RuntimePropertyUpdater:


    BASE_URL = "https://a.blazemeter.com/api/v4"


    def __init__(
        self,
        client,
        config_file,
        discovery_file
    ):

        self.client = client
        self.session = client.session

        self.config_file = config_file
        self.discovery_file = discovery_file



    def load_config(self):

        with open(
            self.config_file,
            "r"
        ) as file:

            return yaml.safe_load(file)



    def load_discovery(self):

        with open(
            self.discovery_file,
            "r"
        ) as file:

            return json.load(file)



    def get_test_id(
        self,
        multitest_name,
        alias
    ):

        discovery = self.load_discovery()


        return (
            discovery[multitest_name]
            ["tests"]
            [alias]
            ["test_id"]
        )



    def get_runtime_properties(
        self,
        multitest_name,
        alias
    ):

        config = self.load_config()


        for project in config["projects"]:

            for multitest in project["multitests"]:


                if multitest["name"] == multitest_name:


                    for test in multitest["performance_tests"]:


                        if test["alias"] == alias:


                            return test.get(
                                "runtime_properties",
                                {}
                            )


        raise Exception(
            f"Runtime properties not found for {alias}"
        )



    def update(
        self,
        multitest_name,
        alias
    ):


        test_id = self.get_test_id(
            multitest_name,
            alias
        )


        properties = self.get_runtime_properties(
            multitest_name,
            alias
        )


        url = (
            f"{self.BASE_URL}/tests/{test_id}"
        )


        logger.info(
            "Getting test %s",
            test_id
        )


        response = self.session.get(
            url
        )


        response.raise_for_status()


        test = response.json()["result"]



        remote_control = []


        for key,value in properties.items():

            remote_control.append(
                {
                    "key": key,
                    "value": str(value)
                }
            )



        test["configuration"]["plugins"]["remoteControl"] = remote_control


        logger.info(
            "Updating test id %s for alias %s",
            test_id,
            alias
        )

        logger.info(
            "Updating JMeter properties"
        )

        logger.info(
        json.dumps(
            remote_control,
            indent=4
        )
    )


        response = self.session.put(
            url,
            json=test
        )


        print("STATUS:")
        print(response.status_code)


        print(response.text)


        response.raise_for_status()


        return response.json()