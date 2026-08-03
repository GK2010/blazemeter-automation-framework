# from scripts.utils import load_config
# from scripts.auth import BlazeMeterClient

# def main():

#     config = load_config()
#     client = BlazeMeterClient(config)
#     user = client.test_connection()

#     if user:
#         print("\n Logged in as : ")
#         print(user)

# if __name__ == "__main__":
#    main()

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
    level=logging.INFO
)


def main():

    config = load_config()

    #-------------------
    # Authenticate
    #-------------------

    client = BlazeMeterClient(
        config
    )


    user = client.test_connection()


    if not user:
        return


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


    print("\nDiscovery Result:")

    # print(
    #     json.dumps(
    #         result,
    #         indent=4
    #     )
    # )

    # -----------------------------
    # Update Multi Test execution
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
            f"\nUpdating {alias}"
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
    # Update runTime Properties
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


    # collection_id = result[
    #     "1x Load Test[DIL] - BFS Client - IMPACT Trades"
    # ][
    #     "collection_id"
    # ]
    for update in config.get("execution_updates", []):

    multitest_name = update["multitest"]


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
        "\nStarting Multi Test:"
    )

    print(
        collection_id
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



if __name__ == "__main__":

    main()