"""The module of the Toniecloud session."""
import requests


class TonieCloudSession(requests.Session):
    """A regular restss session to the TonieCloud REST API."""

    URI: str = "https://api.tonie.cloud/v2"
    OPENID_CONNECT: str = "https://login.tonies.com/auth/realms/tonies/protocol/openid-connect/token"

    def __init__(self):
        """Initialize the session."""
        super().__init__()
        self.token: None | str = None

    def acquire_token(self, username: str, password: str) -> None:
        """Acquire the token from the ToniCloud SSO login using username and password.

        Args:
            username (str): The username
            password (str): The password_
        """
        self.token = self._acquire_token(username, password)

    def _acquire_token(self, username: str, password: str) -> str:
        data = {
            "grant_type": "password",
            "client_id": "my-tonies",
            "scope": "openid",
            "username": username,
            "password": password,
        }
        response = requests.post(self.OPENID_CONNECT, data=data, timeout=15)
        return response.json()["access_token"]
