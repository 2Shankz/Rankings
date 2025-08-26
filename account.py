import json
import requests
import sys

from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from src import cryption
from src import utils

# Creates an account on gb/jp that handles API requests
class Account(object):
    def __init__(self, version):
        self.version = version
        self.user_info = {
            "uuid": utils.generate_uuid(),
            "adid": utils.generate_gaid(),
            "udid": utils.generate_idfa(),
            "session_key": None,
            "bq159_key": None,
            "sakura_session": None,
            "username": None,
            "platform": "ios"
        }
        self.session = requests.Session()
        self.register()

        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount("http://", HTTPAdapter(max_retries=retries))

    # Registers a new user with the server.
    def register(self):
        url = f"{utils.get_api_url(self.version)}/users/register"
        user_data = {
            "uuid": self.user_info["uuid"],
            "country_code": "CA",
            "currency_unit": "CAD",
            "idfa": "00000000-0000-0000-0000-000000000000",
            "locale": "",
            "udid": self.user_info["udid"]
        }
        user_data = json.dumps(user_data)

        # Set initial session key
        key = cryption.create_from_key("vuyWQSjlknpJF54ib36txVse")
        self.user_info["session_key"] = key

        self.update_request_headers()
        encoded_data = cryption.encrypt(key, user_data)
        response = self.session.post(url, json={"encoded": True, "data": encoded_data.decode("utf-8")})
        
        if response.ok:
            self.handle_registration_response(response.json())
            print(f"{self.version} account created successfully")
        else:
            print(response.status_code)
            print("Error during registration.")
            sys.exit(0)

    # Update session headers with default or session-specific authentication.
    def update_request_headers(self, session_id=None):
        headers = {
            "Host": utils.get_api_host(self.version),
            "Content-type": "application/json",
            "Accept": "application/json",
            "User-Agent": utils.get_user_agent(self.version),
            "Authorization": "Basic c2FrdXJhOjBubHkwbmU=",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close"
        }
        if session_id:
            headers["X-SESSION"] = session_id
        self.session.headers.update(headers)

    # Processes server response after registration.
    def handle_registration_response(self, data):
        data = cryption.decrypt(self.user_info["session_key"], data["data"])
        data = json.loads(data.value.decode("utf-8"))
        self.user_info["bq159_key"] = data["bq159_key"]
        self.user_info["session_key"] = cryption.create_from_key(self.user_info["bq159_key"])
        self.user_info["sakura_session"] = data["session_id"]
        self.update_request_headers(self.user_info["sakura_session"])

    # API request
    # Return decrypted data
    def get(self, path):
        data = []
        url = f"{utils.get_api_url(self.version)}/{path}"

        try: response = self.session.get(url)
        except requests.exceptions.HTTPError as error: print ("\t\t" + "Http Error:", error)
        except requests.exceptions.ConnectionError as error: print ("\t\t" + "Connection Error:", error)
        except requests.exceptions.Timeout as error: print ("\t\t" + "Timeout Error:", error)
        except requests.exceptions.RequestException as error: print ("\t\t" + "Other Error:", error)
        else: data = self.decrypt_data(response.json())
        return data
    
    # Capable of decrypting large data
    def decrypt_data(self, data):
        key = cryption.create_from_key(self.user_info["bq159_key"])
        data = data["data"]

        size = 256
        decoded = cryption.decrypt(key, data[:size]).value
        for start in range(size, len(data), size):
            decoded += cryption.decrypt(key, data[start:start+size]).value
        decoded = decoded.decode("utf-8")

        return json.loads(decoded)
    