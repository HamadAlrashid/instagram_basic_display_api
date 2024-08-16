import requests

"""
Instagram Basic Display API helper functions.
These functions are used to interact with the Instagram Basic Display API.

auth_window(): Generates the Instagram authorization URL.
get_short_access_token(): Retrieves the access token from Instagram API using the provided client credentials and authorization code.
exchange_for_long_lived_token(): Exchange a short-lived Instagram Basic Display API access token for a long-lived one.
get_user_profile(): Get user profile data from Instagram Basic Display API.
get_user_media(): Get user media from Instagram Basic Display API.
get_carousel_album_media(): Get the media collection in a carousel album from Instagram Basic Display API.
refresh_access_token(): Refresh the access token.
get_user_media_paging(): Get user media from Instagram Basic Display API using a paging URL.
"""

media_limit_fetch = 20  # Number of media items to fetch per request


def auth_window(client_id, redirect_uri):
    """
    Generates the Instagram authorization URL.

    Args:
        client_id (str): The client ID from the Instagram Developer Dashboard.
        redirect_uri (str): The redirect URI specified in the Instagram Developer Dashboard.

    Returns:
        str: The Instagram authorization URL.
    """
    instagram_auth_url = f"https://api.instagram.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=user_profile,user_media&response_type=code"
    return instagram_auth_url


def get_short_access_token(client_id, client_secret, redirect_uri, code):
    """
    Retrieves the access token from Instagram API using the provided client credentials and authorization code.
    The short-lived access token is valid for 1 hour.

    Args:
        client_id (str): The client ID from the Instagram Developer Dashboard.
        client_secret (str): The client secret from the Instagram Developer Dashboard.
        redirect_uri (str): The redirect URI specified in the Instagram Developer Dashboard.
        code (str): The authorization code received after the user grants access.

    Returns:
        dict: The response JSON containing the access token and expiration time.
    """
    url = "https://api.instagram.com/oauth/access_token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "code": code,
    }
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            "Failed to retrieve access token. Error: {}".format(response.text)
        )


def exchange_for_long_lived_token(short_lived_token, client_secret):
    """
    Exchange a short-lived Instagram Basic Display API access token for a long-lived one.
    The long-lived access token is valid for 60 days.

    Args:
        short_lived_token (str): The short-lived access token.
        client_secret (str): The client secret from the Instagram Developer Dashboard.

    Returns:
        dict: The response JSON containing the long-lived access token and expiration time.
    """

    endpoint = "https://graph.instagram.com/access_token"

    params = {
        "grant_type": "ig_exchange_token",
        "client_secret": client_secret,
        "access_token": short_lived_token,
    }

    response = requests.get(endpoint, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            "Failed to exchange for long-lived token. Error: {}".format(response.text)
        )


def get_user_profile(access_token):
    """
    Get user profile data from Instagram Basic Display API.
    This includes the user's app-scoped ID, username, account type, and media count.

    args:
        access_token (str): The user's access token.

    returns:
        dict: The response JSON containing the user profile data.
    """
    endpoint = "https://graph.instagram.com/me"

    params = {
        "fields": "id,username,account_type,media_count",
        "access_token": access_token,
    }

    response = requests.get(endpoint, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            "Failed to retrieve user profile data. Error: {}".format(response.text)
        )


def get_user_media(access_token):
    """
    Get user media from Instagram Basic Display API.
    This includes caption,id,media_type,media_url,permalink,thumbnail_url,timestamp for each media item.

    Args:
        access_token (str): The user's access token.

    Returns:
        dict: The response JSON containing the user media data.
    """
    endpoint = "https://graph.instagram.com/me/media"

    params = {
        "fields": "caption,id,media_type,media_url,permalink,thumbnail_url,timestamp,username,children{id,media_type,media_url,permalink,thumbnail_url,timestamp}",
        "access_token": access_token,
        "limit": media_limit_fetch,
    }

    response = requests.get(endpoint, params=params)

    limit = 500

    if response.status_code == 200:
        result = response.json()
        # Check if there are more pages of media. If so, fetch them and append to the result.
        if "paging" in result:
            while "next" in result["paging"]:
                if len(result["data"]) >= limit:
                    break
                next_page_url = result["paging"]["next"]
                next_page_data = get_user_media_paging(next_page_url)
                result["data"].extend(next_page_data["data"])
                if "paging" in next_page_data:
                    result["paging"] = next_page_data["paging"]
                else:
                    break

        return result

    else:
        raise Exception(
            "Failed to retrieve user media. Error: {}".format(response.text)
        )


def get_carousel_album_media(album_id, access_token):
    """
    Get the media collection in a carousel album from Instagram Basic Display API.

    Args:
        album_id (str): The ID of the carousel album.
        access_token (str): The user's access token.

    Returns:
        dict: The response JSON containing the carousel album media data.
    """

    endpoint = f"https://graph.instagram.com/{album_id}/children"

    params = {
        "fields": "id,is_shared_to_feed,media_type,media_url,permalink,thumbnail_url,timestamp,username",
        "access_token": access_token,
    }

    response = requests.get(endpoint, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            "Failed to retrieve carousel album media. Error: {}".format(response.text)
        )


def refresh_access_token(long_lived_token):
    """
    Refresh the access token.
    The refreshed access token will have the same expiration time as the original long-lived token.

    Args:
        long_lived_token (str): The long-lived access token.

    Returns:
        dict: The response JSON containing the refreshed access token.
    """
    url = "https://graph.instagram.com/refresh_access_token"

    params = {"grant_type": "ig_refresh_token", "access_token": long_lived_token}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            "Failed to refresh access token. Error: {}".format(response.text)
        )


def get_user_media_paging(next_page_url):
    """
    Get user media from Instagram Basic Display API using a paging URL.

    Args:
        next_page_url (str): The URL for the next page of media.

    Returns:
        dict: The response JSON containing the user media data.
    """
    response = requests.get(next_page_url)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            "Failed to retrieve user media. Error: {}".format(response.text)
        )


if __name__ == "__main__":
    access_token = ""
    media = get_user_media(access_token)
    # print("Media fetched:", media)
