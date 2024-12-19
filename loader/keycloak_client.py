import requests
import logging
from utilities import handle_request_errors, delay


class KeycloakClient:
    def __init__(self, host: str, realm: str, token_type: str, access_token: str):
        self.host = host
        self.realm = realm
        self.headers = {
            "Authorization": f"{token_type} {access_token}",
            "Content-Type": "application/json",
        }
        logging.basicConfig(
            filename="logs.log",
            format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            level=logging.INFO,
        )
        self.__logger = logging.getLogger(__name__)

    @delay(delay_ms=10)
    @handle_request_errors
    def get(self, endpoint: str, params: dict = None) -> dict:
        response = requests.get(
            f"{self.host}{endpoint}", headers=self.headers, params=params
        )
        log = f"GET url: {endpoint}   {str(response.status_code)}"
        self.__logger.info(log)
        response.raise_for_status()
        return response.json()

    @delay(delay_ms=10)
    @handle_request_errors
    def post(self, endpoint: str, data: dict) -> dict:
        response = requests.post(
            f"{self.host}{endpoint}", headers=self.headers, json=data
        )
        log = f"POST url: {endpoint}   {str(response.status_code)}"
        self.__logger.info(log)
        response.raise_for_status()
        return response

    @delay(delay_ms=10)
    @handle_request_errors
    def put(self, endpoint: str, data: dict = None) -> dict:
        response = requests.put(
            f"{self.host}{endpoint}", headers=self.headers, json=data
        )
        log = f"PUT url: {endpoint}   {str(response.status_code)}"
        self.__logger.info(log)
        response.raise_for_status()
        return response

    @handle_request_errors
    def delete(self, endpoint: str, id: str) -> dict:
        response = requests.delete(f"{self.host}{endpoint+id}", headers=self.headers)
