import responses

from tonie_api.session import TonieCloudSession


@responses.activate
def test_session():
    responses._add_from_file("tests/res/session.yaml")
    session = TonieCloudSession()
    session.acquire_token("dummy-user", "pass")
    assert session.token == "eyJhbGci<sometoken>VMRfxtg"
