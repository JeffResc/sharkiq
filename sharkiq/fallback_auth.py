import math
import random
import hashlib
import codecs
import base64
import urllib.parse

OAUTH = {
    "LOGIN_URL": "https://login.sharkninja.com/authorize",
    "CLIENT_ID": "wsguxrqm77mq4LtrTrwg8ZJUxmSrexGi",
    "SCOPES": "openid profile email offline_access read:users read:current_user read:user_idp_tokens",
    "AUTH0_CLIENT": "eyJ2ZXJzaW9uIjoiMi42LjAiLCJuYW1lIjoiQXV0aDAuc3dpZnQiLCJlbnI6eyJpVCI6IjE3LjYiLCJzd2lmdCI6IjUueCJ9fQ=="
}

from .const import (
    AUTH0_URL,
    AUTH0_CLIENT_ID,
    AUTH0_SCOPES,
    AUTH0_REDIRECT_URI,
    AUTH0_CLIENT,
    EU_AUTH0_URL
)

class FallbackAuth:
  def GenerateFallbackAuthURL(europe: bool):
    state = FallbackAuth.generateRandomString(43)
    verification = FallbackAuth.generateRandomString(43)
    challenge = FallbackAuth.generateChallengeB64Hash(verification)
    base_url = EU_AUTH0_URL if europe == True else AUTH0_URL

    url = (base_url + "/authorize?os=ios&response_type=code&mobile_shark_app_version=rn1.01"
    + '&client_id=' + FallbackAuth.urlEncode(AUTH0_CLIENT_ID)
    + '&state=' + FallbackAuth.urlEncode(state)
    + '&scope=' + FallbackAuth.urlEncode(AUTH0_SCOPES)
    + '&redirect_uri=' + FallbackAuth.urlEncode(AUTH0_REDIRECT_URI)
    + '&code_challenge=' + FallbackAuth.urlEncode(challenge)
    + '&screen_hint=signin'
    + '&code_challenge_method=S256'
    + '&ui_locales=en'
    + '&auth0Client=' + AUTH0_CLIENT)
    
    return url

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