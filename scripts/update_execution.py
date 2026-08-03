"""
Responsible for:

update_execution.py

1. Read config.yaml

2. Read discovery.json

3. Find:
      multitest
      alias

4. Convert:
      users
      duration
      ramp_up
      locations

5. Convert location names:
      US East (Virginia)
             |
             v
      us-east4-a

6. Build PUT payload

7. Call:
      /collections/{collection_id}/override-tests-executions
"""

"""
update_execution.py

Purpose:
---------
Update BlazeMeter Multi Test execution settings.

Flow:

config.yaml
      |
      v
execution settings
      |
      v
discovery.json
      |
      v
alias -> index
      |
      v
PUT /collections/{collection_id}/override-tests-executions


No hardcoded indexes.
"""


import json
import yaml
import logging


logger = logging.getLogger(__name__)


class ExecutionUpdater:


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



    def load_yaml(self):

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



    def get_test_index(
            self,
            multitest_name,
            alias
    ):

        """
        Dynamically find BlazeMeter execution index.
        """

        discovery = self.load_discovery()


        multitest = discovery.get(
            multitest_name
        )


        if not multitest:

            raise Exception(
                f"Multi Test not found: {multitest_name}"
            )


        test_info = (
            multitest
            .get("tests", {})
            .get(alias)
        )


        if not test_info:
            raise Exception(
            f"Alias not found: {alias}"
        )


        index = test_info["index"]


        return index



    def get_collection_id(
            self,
            multitest_name
    ):

        discovery = self.load_discovery()


        return (
            discovery
            [multitest_name]
            ["collection_id"]
        )



    def convert_hold_for(
            self,
            duration
    ):

        """
        Convert minutes to BlazeMeter format.

        Example:

        60 -> 59m

        BlazeMeter UI stores
        60 minutes as 59m
        """

        if duration <= 0:

            return "0m"


        return f"{duration-1}m"



    def convert_ramp_up(
            self,
            ramp_up
    ):

        return f"{ramp_up}m"



    def build_payload(
            self,
            execution
    ):

        locations = {}


        for item in execution.get(
            "locations",
            []
        ):

            #
            # Temporary mapping.
            # We will externalize this later.
            #

            blaze_location = item["location"]


            locations[
                blaze_location
            ] = item["users"]



        total_users = execution.get(
            "users"
        )


        payload = {


            "overrideExecutions": [

                {

                    "concurrency": total_users,

                    "executor": "jmeter",

                    "holdFor": self.convert_hold_for(
                        execution["duration"]
                    ),

                    "locations": locations,

                    "locationsPercents": self.calculate_percent(
                        locations
                    ),

                    "rampUp": self.convert_ramp_up(
                        execution["ramp_up"]
                    ),

                    "steps": 0

                }

            ],

            "enableLoadConfiguration": True

        }


        return payload



    def calculate_percent(
            self,
            locations
    ):

        total = sum(
            locations.values()
        )


        result = {}


        for key,value in locations.items():

            result[key] = round(
                value * 100 / total
            )


        return result



    def update(
            self,
            multitest_name,
            alias
    ):


        config = self.load_yaml()


        index = self.get_test_index(
            multitest_name,
            alias
        )


        collection_id = self.get_collection_id(
            multitest_name
        )


        execution = None


        for project in config["projects"]:

            for multitest in project["multitests"]:


                if multitest["name"] == multitest_name:


                    for test in multitest["performance_tests"]:


                        if test["alias"] == alias:

                            execution = test["execution"]



        if not execution:

            raise Exception(
                f"Execution config not found for {alias}"
            )



        payload = self.build_payload(
            execution
        )


        payload["index"] = index



        url = (

            f"{self.BASE_URL}/collections/"
            f"{collection_id}"
            "/override-tests-executions"
            "?populateTests=true"

        )


        logger.info(
            "Updating %s index %s",
            alias,
            index
        )


        logger.info(
            json.dumps(
                payload,
                indent=4
            )
        )



        response = self.session.put(
            url,
            json=payload
        )


        print("\nPUT STATUS:")
        print(response.status_code)


        print("\nPUT RESPONSE:")
        print(response.text)


        response.raise_for_status()


        return response.json()
