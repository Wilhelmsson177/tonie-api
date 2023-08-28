"""The base module of the tonie-api."""

import logging
from enum import Enum
from pathlib import Path
from string import Template

import requests
from requests.exceptions import HTTPError

from tonie_api.models import Chapter, Config, CreativeTonie, FileUploadRequest, Household, User
from tonie_api.session import TonieCloudSession

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class HttpMethod(Enum):
    """An enum of the Http Method to use."""

    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"


class TonieAPI:
    """The TonieAPI class."""

    API_URL = "https://api.tonie.cloud/v2"

    def __init__(self, username: str, password: str) -> None:
        """Initializes the API and creates a session token for tonie cloud session."""
        self.session = TonieCloudSession()
        self.session.acquire_token(username=username, password=password)

    def __request(self, url: str, request_type: HttpMethod, data: dict | None = None) -> dict:
        headers = {"Authorization": f"Bearer {self.session.token}"}
        if not data:
            data = {}
        resp = self.session.request(request_type.name, f"{self.API_URL}/{url}", headers=headers, json=data)
        if not resp.ok:
            log.error("HTTP request failed: %s", resp)
            return {}
        return resp.json()

    def _get(self, url: str) -> dict:
        return self.__request(url, HttpMethod.GET)

    def _post(self, url: str, data: dict | None = None) -> dict:
        if not data:
            data = {}
        return self.__request(url, HttpMethod.POST, data=data)

    def _patch(self, url: str, data: dict | None = None) -> dict:
        if not data:
            data = {}
        return self.__request(url, HttpMethod.PATCH, data=data)

    def get_me(self) -> User:
        """Gets the information about the logged in user.

        Returns:
            User: The user object.
        """
        url = "me"
        return User(**self._get(url))

    def get_config(self) -> Config:
        """Gets the backend configuration.

        Returns:
            User: The config object.
        """
        url = "config"
        return Config(**self._get(url))

    def get_households(self) -> list[Household]:
        """Get all households of the logged in user.

        Returns:
            List[Household]: All Households of user.
        """
        url = "households"
        return [Household(**x) for x in self._get(url)]

    def get_all_creative_tonies_by_household(self, household: Household) -> list[CreativeTonie]:
        """Get all creative tonies by a given household.

        Args:
            household (Household): A household

        Returns:
            Lis[CreativeTonie]: A list of all creative tonies, which belong to the given household.
        """
        url = Template("households/$household_id/creativetonies")
        return [CreativeTonie(**ct) for ct in self._get(url=url.substitute(household_id=household.id))]

    def get_all_creative_tonies(self) -> list[CreativeTonie]:
        """Get all creative tonies of the logged in user.

        Returns:
            List[CreativeTonie]: A list of all creative tonies, which belong to the logged in user.
        """
        url = Template("households/$household_id/creativetonies")
        return [
            CreativeTonie(**ct)
            for household in self.get_households()
            for ct in self._get(url=url.substitute(household_id=household.id))
        ]

    def upload_file_to_tonie(self, creative_tonie: CreativeTonie, file: Path | str, title: str) -> None:
        """Upload file to toniecloud and append as new chapter to tonie.

        Args:
            creative_tonie (CreativeTonie): The tonie on which the file gets uploaded to
            file (Path | str): The path of the file
            title (str): the title for the chapter

        Returns:
            boolean: True if file was successful uploaded.
        """
        # get info and credentials for upload from toniecloud
        upload_request = FileUploadRequest(**self._post("file"))
        log.debug("fileId: %s - fields %s", upload_request.fileId, upload_request.request.fields)
        # upload to Amazon S3
        try:
            with Path(file).open("rb") as _fs:
                r = requests.post(
                    upload_request.request.url,
                    files={
                        **upload_request.request.fields,
                        "file": (upload_request.request.fields["key"], _fs),
                    },
                    timeout=180,
                )
            r.raise_for_status()
        except HTTPError:
            log.exception("HTTP error occurred")
            raise

        # add chapter to creative tonie
        self.add_chapter_to_tonie(creative_tonie, upload_request.fileId, title)

    def add_chapter_to_tonie(self, creative_tonie: CreativeTonie, file_id: str, title: str) -> None:
        """Add a chapter to a given tonie with file_id and title.

        Args:
            creative_tonie (CreativeTonie): The Tonie to add the chapter to
            file_id (str): The file id of the file to add as chapter
            title (str): The title of the chapter
        """
        url = f"households/{creative_tonie.householdId}/creativetonies/{creative_tonie.id}/chapters"
        self._post(url=url, data={"title": title, "file": file_id})

    def sort_chapter_of_tonie(self, creative_tonie: CreativeTonie, sort_list: list[Chapter]) -> None:
        """Sort all chapters of the tonie to the given list.

        Args:
            creative_tonie (CreativeTonie): The Tonie to sort the chapters on.
            sort_list (list[Chapter]): A list of all chapters in the correct order.
        """
        url = f"households/{creative_tonie.householdId}/creativetonies/{creative_tonie.id}"
        self._patch(url=url, data={"chapters": [dict(chapter) for chapter in sort_list]})

    def clear_all_chapter_of_tonie(self, creative_tonie: CreativeTonie) -> None:
        """Clear all chapter of given tonie.

        Args:
            creative_tonie (CreativeTonie): _The tonie to clear all chapters on.
        """
        url = f"households/{creative_tonie.householdId}/creativetonies/{creative_tonie.id}"
        self._patch(url=url, data={"chapters": []})
