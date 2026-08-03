# Only starts the execution.
import logging
import time


logger = logging.getLogger(__name__)


class MultiTestRunner:


    BASE_URL = "https://a.blazemeter.com/api/v4"


    def __init__(self, client):

        self.session = client.session



    def get_multitest_info(self, collection_id):

        url = (
            f"{self.BASE_URL}"
            f"/multi-tests/{collection_id}"
        )


        response = self.session.get(url)

        response.raise_for_status()

        return response.json()



    def get_start_info(self, collection_id):

        url = (
            f"{self.BASE_URL}"
            f"/multi-tests/{collection_id}/info"
            "?isDebugRun=false"
        )


        response = self.session.get(url)

        response.raise_for_status()

        return response.json()



    def start(self, collection_id):


        print(
            "\nPreparing Multi Test..."
        )


        self.get_multitest_info(
            collection_id
        )


        info = self.get_start_info(
            collection_id
        )


        print(
            "\nMulti Test Ready"
        )


        url = (
            f"{self.BASE_URL}"
            f"/multi-tests/{collection_id}/start"
        )


        response = self.session.post(
            url,
            json={}
        )


        print(
            "\nSTART STATUS:",
            response.status_code
        )


        print(
            response.text
        )


        response.raise_for_status()


        return response.json()