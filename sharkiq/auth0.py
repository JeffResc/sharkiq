"""Wrapper to authenticate with Shark IQ API."""

import math
import random
import hashlib
import codecs
import base64
import urllib.parse

from aiohttp import ClientSession

from .const import (
    AUTH0_EU_REDIRECT_URI,
    AUTH0_EU_DOMAIN,
    AUTH0_EU_CLIENT_ID,
    AUTH0_EU_CLIENT,
    AUTH0_DOMAIN,
    AUTH0_CLIENT_ID,
    AUTH0_CLIENT,
    AUTH0_REDIRECT_URI,
    AUTH0_SCOPES
)

def generateURL(is_eu: bool, state: str, challenge: str):
    if is_eu:
        url = AUTH0_EU_DOMAIN
        client_id = AUTH0_EU_CLIENT_ID
        redirect_uri = AUTH0_EU_REDIRECT_URI
        client = AUTH0_EU_CLIENT
    else:
        url = AUTH0_DOMAIN
        client_id = AUTH0_CLIENT_ID
        redirect_uri = AUTH0_REDIRECT_URI
        client = AUTH0_CLIENT
    return (url + "?response_type=code"
    + '&client_id=' + urlEncode(client_id)
    + '&state=' + urlEncode(state)
    + '&scope=' + urlEncode(AUTH0_SCOPES)
    + '&redirect_uri=' + urlEncode(redirect_uri)
    + '&code_challenge=' + urlEncode(challenge)
    + '&code_challenge_method=S256'
    + '&ui_locales=en'
    + '&auth0Client=' + urlEncode(client))

def generateRandomString(length):
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    result = ''
    for _ in range(length):
        randomIndex = math.floor(random.random() * len(characters))
        result += characters[randomIndex]
    return result

def generateChallengeB64Hash(verification_code):
    verification_encoded = codecs.encode(verification_code, 'utf-8')
    verification_sha256 = hashlib.sha256(verification_encoded)
    challenge_b64 = base64.b64encode(verification_sha256.digest()).decode()
    challenge_b64_clean = challenge_b64.replace("+", "-").replace("/", "_").replace("=", "").replace("$", "")
    return challenge_b64_clean

def urlEncode(s):
    return urllib.parse.quote_plus(s)

def _extract_state_code(url: str) -> str:
    """Extract the state code from the given URL."""
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    code = query_params.get("state")
    if not code:
        raise ValueError("State not found in the URL")
    return code[0]

def _extract_callback_code(callback_url: str) -> str:
    """Extract the callback code from the given URL."""
    parsed_url = urllib.parse.urlparse(callback_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    code = query_params.get("code")
    if not code:
        raise ValueError("Callback code not found in the URL")
    return code[0]

## Shark's implementation redirects to the signup page first, which is an odd choice

async def _get_login_state(session: ClientSession, is_eu: bool, state: str, challenge: str) -> str:
    """Retrieve the login state."""
    async with session.get(generateURL(is_eu, state, challenge)) as response:
        if response.status != 200:
            raise Exception(f"Failed to get login state: {response.status}")
        return _extract_state_code(str(response.url))

async def _post_login(session: ClientSession, is_eu: bool,username: str, password: str, state: str):
    """Post login"""
    if is_eu:
        login_url = AUTH0_EU_DOMAIN + "/u/login?ui_locales=en&state=" + state
    else:
        login_url = AUTH0_DOMAIN + "/u/login?ui_locales=en&state=" + state

    async with session.post(
        login_url,
        data={
            "username": username,
            "password": password,
            "action": "default",
            "state": state,
        },
        allow_redirects=False,
        headers={
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36",
            "sec-ch-ua": '"Not_A Brand";v="99", "Chromium";v="133", "Google Chrome";v="133"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "content-type": "application/x-www-form-urlencoded",
            "origin": AUTH0_EU_DOMAIN if is_eu else AUTH0_DOMAIN,
            "referer": login_url,
        }
    ) as response:
        if response.status != 302:
            raise Exception(f"Failed to post login: {response.status}")
        location = response.headers.get("Location")
        if "/u/login" in location:
            raise Exception("Invalid username or password")
        if not location:
            raise Exception("No Location header found in response")
        return location

async def _resume_authorization(session: ClientSession, is_eu: bool, resume_location: str):
    """Resume the authorization process."""
    if is_eu:
        resume_url = AUTH0_EU_DOMAIN + resume_location
    else:
        resume_url = AUTH0_DOMAIN + resume_location
    async with session.get(resume_url, allow_redirects=False) as response:
        if response.status != 302:
            raise Exception(f"Failed to resume authorization: {response.status}")
        location = response.headers.get("Location")
        if "com.sharkninja.shark" not in location:
            raise Exception("Invalid redirect location")
        return location

async def _get_token(session: ClientSession, is_eu: bool, code: str, verifier: str):
    """Get the token using the code."""
    if is_eu:
        token_url = AUTH0_EU_DOMAIN + "/oauth/token"
    else:
        token_url = AUTH0_DOMAIN + "/oauth/token"
    async with session.post(
        token_url,
        json={
            "client_id": AUTH0_EU_CLIENT_ID,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": AUTH0_EU_REDIRECT_URI,
            "code_verifier": verifier,
        },
        allow_redirects=False
    ) as response:
        if response.status != 200:
            raise Exception(f"Failed to get token: {response.status}")
        return await response.json()

async def auth_flow_complete(session: ClientSession, is_eu: bool, username: str, password: str):
    """Complete the authentication flow."""
    state = generateRandomString(43)
    verification = generateRandomString(43)
    challenge = generateChallengeB64Hash(verification)

    # Step 1: Get login state
    login_state = await _get_login_state(session, is_eu, state, challenge)

    # Step 2: Post login
    resume_location = await _post_login(session, is_eu, username, password, login_state)

    # Step 3: Resume Authorization
    resume_location = await _resume_authorization(session, is_eu, resume_location)

    # Step 4: Extract callback code
    code = _extract_callback_code(resume_location)

    # Step 5: Get token
    token_response = await _get_token(session, is_eu, code, verification)
    
    return token_response
