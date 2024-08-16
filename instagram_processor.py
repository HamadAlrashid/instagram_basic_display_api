from datetime import datetime, timedelta
from time import perf_counter
import os
import basic_display_api
from crud.instagram_media import instagram_media_crud
from models.instagram_media import InstagramMedia
from models.types.instagram_media_type import InstagramMediaType
from dotenv import load_dotenv
from social_media_processor import SocialMediaProcessor
from models.user import User
from utils import read_prompt_file, init_db, SessionLocal, call_OAI
import concurrent.futures
import json_validation

"""
    This defines the implementation of a Instagram Processer class, which inherits from the SocialMediaProcessor class.

    The InstagramProcesser takes a User object and an optional authorization code from the Instagram API as input. The auth_code is used to get the Instagram short-term access token and exchange it for a long-lived token.
    If an active token is present in the db, the token is refreshed. If the auth_code is not present and no active token is found, an error is raised.

    The InstagramProcesser has a run method that runs the Instagram Processer.
    It fetches Instagram media data (posts), extracts and preprocesses the data (generate descriptions for the images and albums), saves all media data to the database, do any desired processing & enriching and save the processed data in the db.
"""


env_path = ".env"
load_dotenv(dotenv_path=env_path)

# Load environment variables
INSTAGRAM_CLIENT_ID = os.getenv("INSTAGRAM_CLIENT_ID")
INSTAGRAM_CLIENT_SECRET = os.getenv("INSTAGRAM_CLIENT_SECRET")
INSTAGRAM_AUTH_CALLBACK_URI = os.getenv("INSTAGRAM_AUTH_CALLBACK_URI")
DEBUG = os.getenv("DEBUG") == "1"
DESCRIBE_IMAGE_PROMPT = os.getenv("DESCRIBE_IMAGE_PROMPT")
DESCRIBE_ALBUM_PROMPT = os.getenv("DESCRIBE_ALBUM_PROMPT")
MODEL = os.getenv("MODEL")


def debug(*args, **kwargs):
    if DEBUG:
        print("=" * 10, "DEBUG", "=" * 10)  # noqa
        print(*args, **kwargs)  # noqa
        pass


class InstagramProcesser(SocialMediaProcessor):
    def __init__(self, user: User, auth_code=None):
        super().__init__(user, platform="instagram")
        self.auth_code = auth_code
        self.token = get_instagram_access_token(user.user_id)

        if not self.auth_code and not self.token:
            raise ValueError("Either auth_code or an active token must be present")

        # Get a fresh token if the auth code is present
        if self.auth_code:
            self.authorize()
            self.access_token = get_instagram_access_token(user.user_id)

        else:
            # Refresh the token if it's close to expiry
            # TODO: Implement refresh token logic

            basic_display_api.refresh_access_token(self.token.auth_info["access_token"])
            pass

    def run(self) -> dict:
        """
        Runs the Instagram Processor.

        This function fetches Instagram media data, extracts and preprocesses the data,
        saves the fetched media data to the database, process the data, and prints a completion message.

        Returns:
            dict: return data if the processing process completes successfully. None otherwise.
        """
        try:
            # Fetch the Instagram media data
            media_data = self.fetch_data()

            if not media_data or len(media_data) == 0:
                debug("No new media to fetch.")
                return None
            # Extract and preprocess the media data
            media_objs = self.extract_and_preprocess(media_data)

            if not media_objs or len(media_objs) == 0:
                debug("No new media to process.")
                return None

            # Save the fetched media data to the db
            self.save_data_to_db(media_objs)

            # Process and enrich the data as desired
            result = self.enrich()

            debug("Instagram Processing Complete.")

            return result
        except Exception as e:
            debug(f"Error: {e}")
            return {}

    def authorize(self) -> bool:
        """
        Exhanges the auth code for a long-lived token and inserts the auth info into the db.

        Returns:
            Boolean: True if an active instagram token exists. False otherwise.
        """
        if self.auth_code:
            # Get the Instagram access token and user profile data
            auth_profile_info = get_instagram_access_token_profile_info(self.auth_code)
            self.long_lived_token = auth_profile_info["long_lived_token"]

            # Insert the Instagram auth info to the db.
            update_fields = {
                "auth_info": {
                    "access_token": auth_profile_info["long_lived_token"],
                    "expires_in": auth_profile_info["expires_in"],
                },
                "token_info": auth_profile_info["user_profile_data"],
                "parent_id": None,
            }

            # insert()
            return True

        elif self.token:
            debug("Instagram token exists")
            return True
        else:
            return False

    def fetch_data(self) -> list[json_validation.InstagramMedia]:
        """
        Fetches new Instagram media data from the Instagram API.

        Returns:
            list[InstagramMedia]: a list of raw Instagram media json objects.
        """

        user_media_data = basic_display_api.get_user_media(
            self.token.auth_info["access_token"]
        )

        json_validation.validate_json_types(
            user_media_data, json_validation.InstagramMediaList
        )

        api_fetched_media = user_media_data["data"]

        debug("Fetched Images:", len(api_fetched_media))

        # Fetch the latest media from the db to compare with the media fetched from the API
        with SessionLocal() as db:
            db_fetched_media = (
                instagram_media_crud.get_n_most_recent_media_by_user_id_media_type(
                    db,
                    self.user.user_id,
                    n=1,
                )
            )
        if db_fetched_media:
            db_fetched_media = db_fetched_media[0]
            new_media = []
            for media in api_fetched_media:
                if media["id"] == db_fetched_media.media_id:
                    break
                new_media.append(media)
            return new_media

        else:
            return api_fetched_media

        return api_fetched_media

    def extract_and_preprocess(
        self, data: json_validation.InstagramMedia
    ) -> list[InstagramMedia]:
        """
        Extract and preprocess the Instagram media raw data to construct media objects.
        Generates media description for each media object on the fly.

        Args:
            data (list[json_validation.InstagramMedia]): a list of raw Instagram media json objects.

        Returns:
            list[InstagramMedia]: a list of preprocessed InstagramMedia objects.
        """
        media_objs = construct_instagram_media(self.user.user_id, data)

        debug("Preprocessed Images:", len(media_objs))
        return media_objs

    def save_data_to_db(self, data: list[InstagramMedia]) -> int:
        """
        Saves the fetched Instagram media data to the database.

        Args:
            data (list[InstagramMedia]): a list of preprocessed InstagramMedia objects.

        Returns:
            int: the number of media objects inserted into the db.
        """
        with SessionLocal() as db:
            n = instagram_media_crud.bulk_upsert_media(db, data)
            db.commit()
            return n

    def enrich(self) -> dict:
        """
        Process the data as desired and save it to the database.

        Returns:
            dict: processed data if the processing process completes successfully. None otherwise.
        """
        debug("Processing Instagram data...")

        # Fetch the media data from the db
        with SessionLocal() as db:
            fetched_images = None

            fetched_albums = None

            fetched_videos = None

            fetched_images.extend(fetched_albums)
            fetched_images.extend(fetched_videos)
        debug("Formating media for analysis and post processing...")
        formatted_results = format_crud_results(fetched_images)

        if not formatted_results or len(formatted_results) == 0:
            return None
        try:
            debug("Enriching data ... with {} images".format(len(formatted_results)))

            # Process the data as desired here
            # call_OAI(model=MODEL, messages=messages)

            with SessionLocal() as db:
                debug("Saving result to DB...")

        except Exception as e:
            debug("Error:", e)
            return None
        return {}


def get_instagram_access_token_profile_info(authorization_code: str) -> dict:
    """
    Returns instagram access token and profile info in a json.

    Args:
        authorization_code (str): The authorization code received from the Instagram API.

    Returns:
        dict: a json object containing the long-lived access token and user profile data. None if an error occurs.
    """

    try:
        # Get the short-lived access token

        short_lived_token = basic_display_api.get_short_access_token(
            INSTAGRAM_CLIENT_ID,
            INSTAGRAM_CLIENT_SECRET,
            INSTAGRAM_AUTH_CALLBACK_URI,
            authorization_code,
        )

        json_validation.validate_json_types(
            short_lived_token, json_validation.ShortLivedAccessToken
        )
        debug("Short-lived token:", short_lived_token)

        # Exchange the short-lived token for a long-lived one
        long_lived_token = basic_display_api.exchange_for_long_lived_token(
            short_lived_token["access_token"], INSTAGRAM_CLIENT_SECRET
        )

        json_validation.validate_json_types(
            long_lived_token, json_validation.LongLivedAccessToken
        )

        debug("Long-lived token:", long_lived_token)

        # Get user profile data
        user_profile_data = basic_display_api.get_user_profile(
            long_lived_token["access_token"]
        )

        json_validation.validate_json_types(
            user_profile_data, json_validation.InstagramUserProfile
        )

        debug("User profile data:", user_profile_data)

        return {
            "long_lived_token": long_lived_token["access_token"],
            "expires_in": expiry_to_datetime(long_lived_token["expires_in"]),
            "user_profile_data": user_profile_data,
        }
    except Exception as e:
        debug(f"Error: {e}")
        return None


def construct_instagram_media(
    user_id: str,
    raw_media_list: list[json_validation.InstagramMedia],
    num_workers=14,
) -> list[InstagramMedia]:
    """
    Construct Instagram media objects from raw_media_list.
    Generate media description for each media object.

    Args:
        user_id (str): The user_id associated with the active instagram access token.
        raw_media_list (list[json_validation.InstagramMedia]): a list of raw Instagram media json objects.
        num_workers (int): Optional. The number of worker threads to use for processing the media objects.

    Returns:
        list[InstagramMedia]: a list of preprocessed InstagramMedia objects.
    """

    def worker_process(user_id, raw_media_list):
        media_objs = []
        # Iterate through the raw media list and construct media objects
        for media in raw_media_list:
            # If the media is a carousel album, construct a media object for each child media
            if media.get("media_type") == InstagramMediaType.CAROUSEL_ALBUM.name:
                album_children = media.get("children", {}).get("data", [])

                for child in album_children:
                    # Set the caption of the parent media as the caption of the childs media
                    child["caption"] = media.get("caption")

                    child["media_description"] = get_media_description(child)
                    media_objs.append(
                        _helper_construct_media_from_dict(
                            child,
                            user_id,
                            parent_media_id=media["id"],
                        )
                    )

                # Generate a media description for the whole album
                media["media_description"] = get_album_description(
                    media, album_children=album_children
                )

                # add the parent media object, passing in the list of children media ids
                media_objs.append(
                    _helper_construct_media_from_dict(
                        media,
                        user_id,
                        album_children=[
                            {"id": child["id"]} for child in album_children
                        ],
                    )
                )

            # If the media is not a carousel album (video, or image), construct a media object
            else:
                media["media_description"] = get_media_description(media)
                media_objs.append(_helper_construct_media_from_dict(media, user_id))
            debug("Processed Images:", len(media_objs))

        return media_objs

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        chunk_size = (
            len(raw_media_list) // num_workers
            if len(raw_media_list) > num_workers
            else 1
        )
        batches = list(_chunk(raw_media_list, chunk_size))
        debug("Grouping raw images into batches:", len(batches))

        futures = []
        for batch in batches:
            futures.append(
                executor.submit(
                    worker_process,
                    user_id=user_id,
                    raw_media_list=batch,
                )
            )
        media_objs = []
        for future in concurrent.futures.as_completed(futures):
            media_objs.extend(future.result())

    return media_objs


def _chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def get_instagram_access_token(user_id: str):
    """
    Returns an active Instagram Basic Display API access token for the user.

    Args:
        user_id (str)

    Returns:
        instagram access token: str if exists. None otherwise.
    """

    return None


def expiry_to_datetime(expiry):
    """
    Convert expiry time in seconds to a future datetime object.
    """
    return datetime.now() + timedelta(seconds=expiry)


def _helper_construct_media_from_dict(
    media_dict: dict,
    user_id,
    parent_media_id=None,
    album_children=None,
):
    return InstagramMedia(
        user_id=user_id,
        media_id=media_dict["id"],
        publish_timestamp=datetime.fromisoformat(media_dict["timestamp"]),
        media_type=media_dict["media_type"],
        media_url=media_dict["media_url"],
        media_description=media_dict.get("media_description"),
        permalink=media_dict.get("permalink"),
        thumbnail_url=media_dict.get("thumbnail_url"),
        caption=media_dict.get("caption"),
        album_children=album_children,
        parent_media_id=parent_media_id,
        # embeddings=media_dict.get("embeddings"),
    )


def get_media_description(media: json_validation.InstagramMedia) -> str:
    """
    Generate a media_description for an instagram media (ONLY IMAGES).

    Args:
        media (json_validation.InstagramMedia): an instagram media json object.

    Returns:
        str: a text media description. None if an error occurs.
    """

    if media["media_type"] == InstagramMediaType.IMAGE.value:
        # Create a Media object
        media_url = media["media_url"]
        return _get_image_description(
            image_url=media_url,
            image_caption=media.get("caption"),
            publish_timestamp=media.get("timestamp"),
        )
    else:
        return None


def _get_image_description(
    image_url: str, image_caption=None, publish_timestamp=None
) -> str:
    """
    Get a description of the image using the image URL.

    Args:
        image_url (str): The URL of the image.
        image_caption (str): Optional. The caption of the image.

    Returns:
        str: A text media description. None if an error occurs.
    """
    system_message = read_prompt_file(DESCRIBE_IMAGE_PROMPT)

    image_message = {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {"url": image_url, "detail": "high"},
            }
        ],
    }

    if image_caption:
        image_message["content"].append(
            {
                "type": "text",
                "text": "Image Caption: " + image_caption,
            }
        )

    if publish_timestamp:
        image_message["content"].append(
            {
                "type": "text",
                "text": "Image Publish Timestamp: " + publish_timestamp,
            }
        )

    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": system_message,
                },
            ],
        },
        image_message,
    ]
    try:
        response = call_OAI(
            model=MODEL,
            messages=messages,
        )
        response_message = response.choices[0].message
        image_description = response_message.content
    except Exception as e:
        debug(f"Error: {e}")
        image_description = None
    return image_description if image_description else None


def get_album_description(
    album_media: InstagramMedia, album_children: list[dict]
) -> str:
    """
    Generate a media_description for an instagram album.

    Args:
        album_media (InstagramMedia): an instagram media object.
        album_children (list[dict]): a list of children media objects.

    Returns:
        str: a text description of the album. None if an error occurs.
    """

    """Get a description of the image using the image URL."""
    system_message = read_prompt_file(DESCRIBE_ALBUM_PROMPT)

    try:
        images = {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": child["media_url"], "detail": "high"},
                }
                for child in album_children
                if child["media_type"] == InstagramMediaType.IMAGE.value
            ],
        }

        if album_media.get("caption"):
            images["content"].append(
                {
                    "type": "text",
                    "text": "Album Caption: " + album_media.get("caption"),
                }
            )

        if album_media.get("publish_timestamp"):
            images["content"].append(
                {
                    "type": "text",
                    "text": "Album Publish Timestamp: "
                    + album_media.get("publish_timestamp"),
                }
            )

        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_message,
                    },
                ],
            },
            images,
        ]
        response = call_OAI(
            model=MODEL,
            messages=messages,
        )
        response_message = response.choices[0].message
        image_description = response_message.content
    except Exception as e:
        debug(f"Error: {e}")
        image_description = None
    return image_description if image_description else None


def format_crud_results(query_results: list[InstagramMedia]) -> list:
    """
    Format the fetched media into a list of dictionaries.

    Args:
        query_results (list[InstagramMedia]): a list of InstagramMedia objects.

    Returns:
        list: a list of formatted media dictionaries for enriching.
    """
    formatted_results = []
    for media in query_results:
        try:
            if media.media_type == InstagramMediaType.IMAGE.value:
                formatted_results.append(
                    {
                        "image_description": media.media_description,
                    }
                )
            elif media.media_type == InstagramMediaType.CAROUSEL_ALBUM.value:
                formatted_results.append(
                    {
                        "album_description": media.media_description,
                    }
                )
        except Exception as e:
            debug(f"[ERROR] {e}")
            continue

    return formatted_results


if __name__ == "__main__":
    engine = init_db()
    SessionLocal.configure(bind=engine)

    user = User(
        user_id="UUID",
        email="email",
        name="Hamad",
    )
    start = perf_counter()
    instagram_processor = InstagramProcesser(user)
    instagram_processor.run()
    end = perf_counter()
    debug("Time taken: ", end - start)
