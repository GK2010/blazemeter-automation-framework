"""
discovery.py

Purpose:
--------
Discover BlazeMeter Multi Test execution indexes.

BlazeMeter Multi Test update API uses execution index:

PUT /api/v4/collections/{collection_id}/override-tests-executions

Example:

{
    "index": 1,
    "overrideExecutions": [
        {
            "concurrency": 15
        }
    ]
}


Flow:

config.yaml
    |
    v
collection_id
    |
    v
GET collection
    |
    v
testsForExecutions[]
    |
    v
testId
    |
    v
GET /tests/{testId}
    |
    v
match blaze_test_name
    |
    v
alias -> index


Example output:

{
    "1x Load Test[DIL] - BFS Client - IMPACT Trades": {

        "collection_id": 10506120,

        "tests": {

            "CreateTrade_Impact": 0,
            "AmendTrade_Impact": 1,
            "CancelTrade_Impact": 2

        }
    }
}
"""


import json
import logging
import os
from scripts.utils import load_config

logger = logging.getLogger(__name__)


class BlazeMeterDiscovery:


    BASE_URL = "https://a.blazemeter.com/api/v4"


    def __init__(
            self,
            client,
            config_file: str
    ):

        self.client = client
        self.session = client.session
        self.config_file = config_file




    def get_collection(
            self,
            collection_id
    ):

        """
        Get BlazeMeter Multi Test collection.

        Response contains:

        result.testsForExecutions
        """

        url = (
            # f"{self.client.base_url}/collections/"
            f"{self.client.base_url}/api/v4/collections/"
            f"{collection_id}"
            "?populateTests=true"
        )


        logger.info(
            "Getting collection %s",
            collection_id
        )


        response = self.session.get(
            url,
            timeout=30
        )
        # logger.info("Response status: %s", response.status_code)
        # logger.info("Response headers: %s", response.headers)
        # logger.info("Response body: %s", response.text[:500])
        response.raise_for_status()


        try:
            data = response.json()
        except ValueError:
            logger.error("Invalid JSON response from Blazemeter")
            logger.error(response.text[:500])
            raise


        self.save_debug(
            data,
            "collection_response.json"
        )


        return data



    def get_test_details(
            self,
            test_id
    ):

        """
        Get Performance Test details.
        """

        url = (
            # f"{self.BASE_URL}/tests/"
            f"{self.client.base_url}/api/v4/tests/"
            f"{test_id}"
        )


        logger.info(
            "Getting test details %s",
            test_id
        )

        logger.info(
            "Test details URL: %s",
        url
        )


        response = self.session.get(
            url,
            timeout=30
        )

        logger.info(
            "Response content type: %s",
            response.headers.get("Content-Type")
        )

        logger.info(
            "Response body: %s",
            response.text[:500]
        )

        response.raise_for_status()


        try:
            data = response.json()
        except ValueError:
            logger.error("Invalid JSON response from Blazemeter")
            logger.error(response.text[:500])
            raise


        return data



    def discover(self):

        """
        Main discovery process.
        """

        config = load_config()


        result = {}


        for project in config.get(
            "projects",
            []
        ):


            for multitest in project.get(
                "multitests",
                []
            ):


                collection_id = multitest.get(
                    "collection_id"
                )


                if not collection_id:

                    raise Exception(
                        "collection_id missing"
                    )


                logger.info(
                    "Discovering %s",
                    multitest.get("name")
                )


                collection = self.get_collection(
                    collection_id
                )


                execution_tests = self.extract_tests(
                    collection
                )


                mapping = self.map_tests(
                    multitest.get(
                        "performance_tests",
                        []
                    ),
                    execution_tests
                )


                result[
                    multitest["name"]
                ] = {

                    "collection_id": collection_id,

                    "tests": mapping

                }


        return result



    def extract_tests(
            self,
            response
    ):

        """
        Extract execution ordered tests.

        BlazeMeter response:

        result:
            testsForExecutions:
                [
                    {
                       testId: xxxx
                    }
                ]
        """


        tests = (
            response
            .get("result", {})
            .get("testsForExecutions")
        )


        if isinstance(
                tests,
                list
        ):

            return tests


        raise Exception(
            "Could not find testsForExecutions"
        )



    def map_tests(
            self,
            yaml_tests,
            blaze_tests
    ):

        """
        Create:

        alias -> index

        """

        mapping = {}


        for index, execution_test in enumerate(
                blaze_tests
        ):


            test_id = execution_test.get(
                "testId"
            )


            if not test_id:
                continue



            test_details = self.get_test_details(
                test_id
            )


            blaze_name = (

                test_details
                .get("result", {})
                .get("name")

            )


            logger.info(
                "Index %s = %s",
                index,
                blaze_name
            )


            for yaml_test in yaml_tests:


                alias = yaml_test.get(
                    "alias"
                )


                expected_name = yaml_test.get(
                    "blaze_test_name"
                )


                if self.names_match(
                    expected_name,
                    blaze_name
                ):


                    #mapping[alias] = index
                    mapping[alias] = {
                        "index": index,
                        "test_id": test_id
                    }


                    logger.info(
                        "%s -> %s",
                        alias,
                        index
                    )



        missing = [

            test["alias"]

            for test in yaml_tests

            if test["alias"] not in mapping

        ]


        if missing:

            raise Exception(
                f"Could not discover tests: {missing}"
            )


        return mapping



    def names_match(
            self,
            yaml_name,
            blaze_name
    ):

        """
        Normalize names before comparison.
        """

        if not yaml_name or not blaze_name:

            return False


        return (
            yaml_name.strip()
            .lower()
            ==
            blaze_name.strip()
            .lower()
        )



    def save_result(
            self,
            result,
            output_file
    ):

        os.makedirs(
            os.path.dirname(output_file),
            exist_ok=True
        )


        with open(
            output_file,
            "w"
        ) as file:

            json.dump(
                result,
                file,
                indent=4
            )



    def save_debug(
            self,
            data,
            filename
    ):

        os.makedirs(
            "logs",
            exist_ok=True
        )


        with open(
            f"logs/{filename}",
            "w"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )



if __name__ == "__main__":


    from scripts.utils import load_config
    from scripts.auth import BlazeMeterClient


    logging.basicConfig(
        level=logging.INFO
    )


    config = load_config()


    client = BlazeMeterClient(
        config
    )


    discovery = BlazeMeterDiscovery(

        client,

        "config/config.yaml"

    )


    result = discovery.discover()


    discovery.save_result(

        result,

        "logs/discovery.json"

    )


    print(
        json.dumps(
            result,
            indent=4
        )
    )