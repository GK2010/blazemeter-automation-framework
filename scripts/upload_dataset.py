"""
create.csv
amend.csv
cancel.csv

"""

import json
import yaml
import logging
import os


logger = logging.getLogger(__name__)


class DatasetUploader:


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



    def get_dataset_path(
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

                            return test["dataset"]



        raise Exception(
            f"Dataset not found for {alias}"
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


        dataset = self.get_dataset_path(
            multitest_name,
            alias
        )


        if not os.path.exists(dataset):

            raise Exception(
                f"Dataset file missing: {dataset}"
            )


        url = (
            f"{self.BASE_URL}"
            f"/tests/{test_id}/files"
        )


        logger.info(
            "Uploading %s to test %s",
            dataset,
            test_id
        )

        logger.info(
            "POST %s",
            url
        )

        with open(
            dataset,
            "rb"
        ) as file:


            response = self.session.post(
                url,
                files={
                    "file": file
                },
                headers={
                    "Content-Type": None
                }

            )


        print("\nUPLOAD STATUS:")
        print(response.status_code)


        print(response.text)

        print("\nREQUEST CONTENT TYPE:")
        print(response.request.headers.get("Content-Type"))
        response.raise_for_status()


        return response.json()



    def validate(
        self,
        multitest_name,
        alias
    ):


        dataset = self.get_dataset_path(
            multitest_name,
            alias
        )


        filename = os.path.basename(
            dataset
        )


        test_id = self.get_test_id(
            multitest_name,
            alias
        )


        url = (
            f"{self.BASE_URL}"
            f"/tests/{test_id}/validate"
        )


        payload = {

            "files":[
                {
                    "fileName": filename
                }
            ],

            "performDataMerge": False

        }

        logger.info(
            "POST %s",
            url
        )

        response = self.session.post(
            url,
            json=payload
        )


        print("\nVALIDATION STATUS:")
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


    uploader = DatasetUploader(

        client,

        "config/config.yaml",

        "logs/discovery.json"

    )


    upload_response = uploader.upload(
        "1x Load Test[DIL] - BFS Client - IMPACT Trades",
        "ListTrade_Impact"
    )
    print("\nDataset upload completed successfully")


    validation_response = uploader.validate(
        "1x Load Test[DIL] - BFS Client - IMPACT Trades",
        "ListTrade_Impact"
    )

    print("\nDataset validation completed successfully")

    """