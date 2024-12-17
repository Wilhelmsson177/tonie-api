import datetime

import pytest
import responses

from tonie_api.api import TonieAPI
from tonie_api.models import Config, CreativeTonie, User


@pytest.fixture(autouse=True)
def mocked_responses():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps._add_from_file("tests/res/cloudapi.yaml")
        yield rsps


def test_me():
    tonie_api = TonieAPI("some user", "some_pass")
    user = tonie_api.get_me()
    assert isinstance(user, User)
    assert user.uuid == "fea83d4b-2041-115e5a3"
    assert user.email == "someone@example.com"


def test_config():
    tonie_api = TonieAPI("some user", "some_pass")
    config = tonie_api.get_config()
    assert isinstance(config, Config)
    assert config.locales == ["de", "en", "en_US", "fr"]
    assert config.unicodeLocales == ["de", "en", "en-US", "fr"]
    assert config.accepts == ["aac", "aif", "aiff", "flac", "mp3", "m4a", "m4b", "wav", "oga", "ogg", "opus", "wma"]
    assert config.maxBytes == 1073741824
    assert config.maxChapters == 99
    assert config.maxSeconds == 5400
    assert config.ssoEnabled
    assert not config.stageWarning
    assert config.paypalClientId == "ATXc<some_key>_uQ"


def test_households():
    tonie_api = TonieAPI("some user", "some_pass")
    households = tonie_api.get_households()
    assert isinstance(households, list)
    assert len(households) == 1
    household = households[0]
    assert household.id == "abcd-123456"
    assert household.name == "John Does Household"
    assert household.canLeave
    assert household.ownerName == "John"
    assert household.access == "owner"


def test_creative_tonies():
    tonie_api = TonieAPI("some user", "some_pass")
    creative_tonies = tonie_api.get_all_creative_tonies()
    assert isinstance(creative_tonies, list)
    assert len(creative_tonies) == 5


def test_creative_tonies_by_household():
    tonie_api = TonieAPI("some user", "some_pass")
    household = tonie_api.get_households()[0]
    creative_tonies = tonie_api.get_all_creative_tonies_by_household(household)
    assert isinstance(creative_tonies, list)
    assert len(creative_tonies) == 5


def test_creative_tonie():
    tonie_api = TonieAPI("some user", "some_pass")
    household = tonie_api.get_households()[0]
    creative_tonie = tonie_api.get_all_creative_tonies_by_household(household)[1]
    assert isinstance(creative_tonie, CreativeTonie)
    assert creative_tonie.lastUpdate == datetime.datetime(2023, 4, 2, 18, 32, 58, tzinfo=datetime.UTC)
    assert creative_tonie.secondsPresent == 2057
    assert creative_tonie.secondsRemaining == 3342
    assert creative_tonie.chaptersPresent == 12
    assert creative_tonie.chaptersRemaining == 87
    assert creative_tonie.name == "Kreativ-Tonie"
    assert len(creative_tonie.chapters) == 12
    assert creative_tonie.chapters[0].id == "a2382077-47ba-a03b-d3cff1a371b1"
    assert creative_tonie.chapters[0].file == "4c3b5023599ef85f7b1a87ee7_a2382077-b8b2-a03b-d3cff1a371b1"
    assert creative_tonie.chapters[0].title == "Dr.Brum-verrückt"
    assert creative_tonie.chapters[0].seconds == 392.515563
    assert not creative_tonie.chapters[0].transcoding


def test_upload_file(mocked_responses: responses.RequestsMock):
    tonie_api = TonieAPI("some user", "some_pass")
    household = tonie_api.get_households()[0]
    creative_tonie = tonie_api.get_all_creative_tonies_by_household(household)[0]
    tonie_api.upload_file_to_tonie(creative_tonie, "tests/res/chapter.mp3", "chapter")
    assert mocked_responses.assert_call_count("https://api.tonie.cloud/v2/file", 1) is True
    assert (
        mocked_responses.assert_call_count(
            "https://api.tonie.cloud/v2/households/abcd-123456/creativetonies/CREATIVETONIE_ID/chapters",
            1,
        )
        is True
    )


def test_sort_chapter(mocked_responses: responses.RequestsMock):
    tonie_api = TonieAPI("some user", "some_pass")
    household = tonie_api.get_households()[0]
    creative_tonie = tonie_api.get_all_creative_tonies_by_household(household)[0]
    tonie_api.sort_chapter_of_tonie(creative_tonie, [])
    assert (
        mocked_responses.assert_call_count(
            "https://api.tonie.cloud/v2/households/abcd-123456/creativetonies/CREATIVETONIE_ID",
            1,
        )
        is True
    )


def test_clear_all_chapter(mocked_responses: responses.RequestsMock):
    tonie_api = TonieAPI("some user", "some_pass")
    household = tonie_api.get_households()[0]
    creative_tonie = tonie_api.get_all_creative_tonies_by_household(household)[0]
    tonie_api.clear_all_chapter_of_tonie(creative_tonie)
    assert (
        mocked_responses.assert_call_count(
            "https://api.tonie.cloud/v2/households/abcd-123456/creativetonies/CREATIVETONIE_ID",
            1,
        )
        is True
    )
