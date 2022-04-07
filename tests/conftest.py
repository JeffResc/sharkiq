import pytest
import os
from sharkiq.ayla_api import get_ayla_api


@pytest.fixture
def dummy_api():
    username = "myusername@mysite.com"
    password = "mypassword"

    return get_ayla_api(username=username, password=password)


@pytest.fixture
def sample_api():
    username = os.getenv("SHARKIQ_USERNAME")
    password = os.getenv("SHARKIQ_PASSWORD")

    assert username is not None, "SHARKIQ_USERNAME environment variable unset"
    assert password is not None, "SHARKIQ_PASSWORD environment variable unset"

    return get_ayla_api(username=username, password=password)


@pytest.fixture
def sample_api_logged_in(sample_api):
    sample_api.sign_in()
    return sample_api
