"""The module of the Toniecloud session."""
import requests
from requests.exceptions import Timeout, RequestException


class TonieCloudSession(requests.Session):
    """A regular restss session to the TonieCloud REST API."""

    URI: str = "https://api.tonie.cloud/v2"
    OPENID_CONNECT: str = "https://login.tonies.com/auth/realms/tonies/protocol/openid-connect/token"

    def __init__(self):
        """Initialize the session."""
        super().__init__()
        self.token: None | str = None

    def acquire_token(self, username: str, password: str, timeout: int = 30) -> None:
        """Acquire the token from the ToniCloud SSO login using username and password.

        Args:
            username (str): The username
            password (str): The password_
            timeout (int): The request timeout. Try to increase this value if you receive a timeout error
        """
        self.token = self._acquire_token(username, password,timeout)

    def _acquire_token(self, username: str, password: str, timeout: int) -> str | None:
        data = {
            "grant_type": "password",
            "client_id": "my-tonies",
            "scope": "openid",
            "username": username,
            "password": password,
        }
        try:
            response = requests.post(self.OPENID_CONNECT, data=data, timeout=timeout)
            response.raise_for_status()
            return response.json().get("access_token")
        except Timeout:
            print(f"Request to acquire token timed out.")
        except RequestException as e:
            print(f"An error occurred while acquiring the token: {e}")
        return None
