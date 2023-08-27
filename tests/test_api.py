from tonie_api import TonieAPI


def test_init():
    tonie_api = TonieAPI("dummy_user", "dummy_password")
    assert tonie_api
