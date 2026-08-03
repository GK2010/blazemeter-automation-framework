import json
import yaml
import logging
import os


logger = logging.getLogger(__name__)


class TestScriptUploader:


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



    def get_script_path(
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

                            return test["script"]



        raise Exception(
            f"Test script not found for {alias}"
        )



    def upload(
        self,
        multitest_name,
        alias
    ):


        test_id = self.get_test_id(
            multitest_name,
            alias
        )


        script = self.get_script_path(
            multitest_name,
            alias
        )


        if not os.path.exists(script):

            raise Exception(
                f"Test script missing: {script}"
            )



        url = (
            f"{self.BASE_URL}"
            f"/tests/{test_id}/files"
        )


        logger.info(
            "Uploading test script %s to test %s",
            script,
            test_id
        )


        logger.info(
            "POST %s",
            url
        )



        with open(
            script,
            "rb"
        ) as file:


            response = self.session.post(

                url,

                files={
                    "file": file
                },

                # Important:
                # remove JSON content type inherited from session
                headers={
                    "Content-Type": None
                }

            )


        print("\nTEST SCRIPT UPLOAD STATUS:")
        print(response.status_code)

        print(response.text)


        response.raise_for_status()


        return response.json()

"""
Below block is to run standalone py file
"""
"""
if __name__ == "__main__":


    import logging

    from scripts.utils import load_config
    from scripts.auth import BlazeMeterClient


    logging.basicConfig(
        level=logging.INFO
    )


    config = load_config()


    client = BlazeMeterClient(
        config
    )


    uploader = TestScriptUploader(

        client,

        "config/config.yaml",

        "logs/discovery.json"

    )


    uploader.upload(

        "1x Load Test[DIL] - BFS Client - IMPACT Trades",

        "ListTrade_Impact"

    )
    """