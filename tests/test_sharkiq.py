import aiohttp
import pytest
from sharkiq.ayla_api import get_ayla_api, AylaApi
from sharkiq.const import SHARK_APP_ID, SHARK_APP_SECRET
from sharkiq.exc import SharkIqAuthError
from datetime import datetime, timedelta


def test_get_ayla_api():
    api = get_ayla_api("myusername@mysite.com", "mypassword")

    assert api._email == "myusername@mysite.com"
    assert api._password == "mypassword"
    assert api._access_token is None
    assert api._refresh_token is None
    assert api._auth_expiration is None
    assert api._is_authed == False
    assert api._app_id == SHARK_APP_ID
    assert api._app_secret == SHARK_APP_SECRET
    assert api.websession is None


class TestAylaApi:
    def test_init__required_vals(self):
        api = AylaApi(
            "myusername@mysite.com", "mypassword", "app_id_123", "appsecret_123"
        )

        assert api._email == "myusername@mysite.com"
        assert api._password == "mypassword"
        assert api._access_token is None
        assert api._refresh_token is None
        assert api._auth_expiration is None
        assert api._is_authed == False
        assert api._app_id == "app_id_123"
        assert api._app_secret == "appsecret_123"
        assert api.websession is None

    @pytest.mark.asyncio
    async def test_ensure_session(self, dummy_api):
        # Initially created with no websession
        assert dummy_api.websession is None

        session = await dummy_api.ensure_session()

        # Check that session was created and returned
        assert isinstance(session, aiohttp.ClientSession)
        assert dummy_api.websession is session

    def test_property__login_data(self, dummy_api):
        assert dummy_api._login_data == {
            "user": {
                "email": "myusername@mysite.com",
                "password": "mypassword",
                "application": {
                    "app_id": SHARK_APP_ID,
                    "app_secret": SHARK_APP_SECRET,
                },
            }
        }

    def test_set_credentials__404_response(self, dummy_api):
        with pytest.raises(SharkIqAuthError) as e:
            dummy_api._set_credentials(404, {"error": {"message": "Not found"}})
        assert (
            e.value.args[0] == "Not found (Confirm app_id and app_secret are correct)"
        )

    def test_set_credentials__401_response(self, dummy_api):
        with pytest.raises(SharkIqAuthError) as e:
            dummy_api._set_credentials(401, {"error": {"message": "Unauthorized"}})
        assert e.value.args[0] == "Unauthorized"

    def test_set_credentials__valid_response(self, dummy_api):
        assert dummy_api._access_token is None
        assert dummy_api._refresh_token is None
        assert dummy_api._auth_expiration is None
        assert dummy_api._is_authed == False

        t1 = datetime.now() + timedelta(seconds=3600)
        dummy_api._set_credentials(
            200,
            {
                "access_token": "token123",
                "refresh_token": "token321",
                "expires_in": 3600,
            },
        )

        assert dummy_api._access_token == "token123"
        assert dummy_api._refresh_token == "token321"
        assert dummy_api._auth_expiration.timestamp() == pytest.approx(t1.timestamp())
        assert dummy_api._is_authed == True

    def test_property__sign_out_data(self, dummy_api):
        assert dummy_api.sign_out_data == {
            "user": {"access_token": dummy_api._access_token}
        }

    def test_clear_auth(self, dummy_api): 
        # populate auth values
        assert dummy_api._is_authed == False
        dummy_api._set_credentials(
            200,
            {
                "access_token": "token123",
                "refresh_token": "token321",
                "expires_in": 3600,
            },
        )

        assert dummy_api._is_authed == True 

        dummy_api._clear_auth()

        assert dummy_api._access_token is None
        assert dummy_api._refresh_token is None
        assert dummy_api._auth_expiration is None
        assert dummy_api._is_authed == False
