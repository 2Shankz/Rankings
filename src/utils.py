import uuid

# Return Identifier for Advertiser (IDFA) for iOS account creation. (UDID)
def generate_idfa():
    return str(uuid.uuid4()).upper()

# Return Google Advertising ID (GAID) for Android account creation. (ADID)
def generate_gaid():
    return str(uuid.uuid1())

# Generates UniqueID  for account creation. (UUID)
def generate_uuid():
    return str(uuid.uuid4()) 

# Returns the full API URL based on the version.
def get_api_url(version):
    return "https://app.gb.onepiece-tc.jp" if version == "gb" else "https://app.onepiece-tc.jp"

# Returns the API host based on the version.
def get_api_host(version):
    return "app.gb.onepiece-tc.jp" if version == "gb" else "app.onepiece-tc.jp"

# Returns the user agent based on platform and version.
def get_user_agent(platform, now_version="14.0.0"):
    return f"sakura/{now_version} ({platform}; 7.1.2; SM-G935F)" if platform == "android" else f"sakura/{now_version} (iPhone; iOS 15.3.1; iPhone14,5)"