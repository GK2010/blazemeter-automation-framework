from scripts.utils import load_config
from scripts.auth import BlazeMeterClient
from scripts.discovery import BlazeMeterDiscovery
from scripts.update_execution import ExecutionUpdater
from scripts.update_runtime_properties import RuntimePropertyUpdater
from scripts.multitest_runner import MultiTestRunner
from scripts.upload_dataset import DatasetUploader
from scripts.upload_testscripts import TestScriptUploader

from pathlib import Path

import json
import logging
import sys


config_file = Path("config/config.yaml")


if not config_file.exists():
    print(
        "Missing config/config.yaml\n"
        "Please copy config/config.template.yaml "
        "to config/config.yaml and update your credentials."
    )
    sys.exit(1)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


def main():

    # -----------------------------
    # Load Configuration
    # -----------------------------

    config = load_config()


    # -----------------------------
    # Authenticate
    # -----------------------------

    client = BlazeMeterClient(
        config
    )


    user = client.test_connection()


    if not user:
        print("Authentication failed")
        sys.exit(1) #this is for jenkins as jenkis need exit code. if running local you can use return and comment this
        # return


    print("\nLogged in as:")
    print(user)


    # -----------------------------
    # Discover Multi Test
    # -----------------------------

    discovery = BlazeMeterDiscovery(
        client,
        "config/config.yaml"
    )


    result = discovery.discover()


    discovery.save_result(
        result,
        "logs/discovery.json"
    )


    print("\nDiscovery completed")


    # -----------------------------
    # Update Multi Test Execution
    # Users / Duration / Location
    # -----------------------------

    updater = ExecutionUpdater(
        client,
        "config/config.yaml",
        "logs/discovery.json"
    )


    for update in config.get("execution_updates", []):

        multitest_name = update["multitest"]
        alias = update["test_alias"]


        print(
            f"\nUpdating execution for {alias}"
        )


        response = updater.update(
            multitest_name,
            alias
        )


        print(
            json.dumps(
                response,
                indent=4
            )
        )


    # -----------------------------
    # Update Runtime Properties
    # -----------------------------

    runtime = RuntimePropertyUpdater(
        client,
        "config/config.yaml",
        "logs/discovery.json"
    )


    for update in config.get("execution_updates", []):

        multitest_name = update["multitest"]
        alias = update["test_alias"]


        print(
            f"\nUpdating Runtime Properties for {alias}"
        )


        response = runtime.update(
            multitest_name,
            alias
        )


        print(
            json.dumps(
                response,
                indent=4
            )
        )


    # -----------------------------
    # Upload Test Scripts
    # -----------------------------

    script_uploader = TestScriptUploader(
        client,
        "config/config.yaml",
        "logs/discovery.json"
    )


    # -----------------------------
    # Upload Datasets
    # -----------------------------

    dataset_uploader = DatasetUploader(
        client,
        "config/config.yaml",
        "logs/discovery.json"
    )


    for update in config.get("execution_updates", []):

        multitest_name = update["multitest"]
        alias = update["test_alias"]


        print(
            f"\nUploading Test Script for {alias}"
        )


        script_response = script_uploader.upload(
            multitest_name,
            alias
        )


        print(
            json.dumps(
                script_response,
                indent=4
            )
        )


        print(
            f"\nUploading Dataset for {alias}"
        )


        dataset_response = dataset_uploader.upload(
            multitest_name,
            alias
        )


        print(
            json.dumps(
                dataset_response,
                indent=4
            )
        )


        print(
            f"\nValidating Dataset for {alias}"
        )


        validation_response = dataset_uploader.validate(
            multitest_name,
            alias
        )


        print(
            json.dumps(
                validation_response,
                indent=4
            )
        )


    # -----------------------------
    # Start Multi Test
    # -----------------------------

    runner = MultiTestRunner(
        client
    )


    started_tests = set()

    for update in config.get("execution_updates", []):

        multitest_name = update["multitest"]

        if multitest_name in started_tests:
            continue

        started_tests.add(
            multitest_name
        )

        collection_id = result[
            multitest_name
        ][
            "collection_id"
        ]

        print(
            f"\nStarting Multi Test: {multitest_name}"
        )

        start_response = runner.start(
            collection_id
        )

        print(
            "\nSTART RESPONSE:"
        )

        print(
            json.dumps(
                start_response,
                indent=4
            )
        )

# to run local
# if __name__ == "__main__":

#     main()

# To run from jenkins use below
if __name__ == "__main__":
    try:
        main()
        sys.exit(0)

    except Exception as e:
        logging.exception(e)
        sys.exit(1)