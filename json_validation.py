import logs
from datetime import datetime
from typing import Union, List, Type
from pydantic import BaseModel, ValidationError

logger = logs.get_logger(__name__)


class ShortLivedAccessToken(BaseModel):
    access_token: str


class LongLivedAccessToken(BaseModel):
    access_token: str
    expires_in: int


class InstagramUserProfile(BaseModel):
    id: str
    username: str
    account_type: str
    media_count: int


class InstagramAuthInfo(BaseModel):
    access_token: str
    expires_in: int


class InstagramMedia(BaseModel):
    id: str
    timestamp: datetime
    media_type: str
    media_url: str


class InstagramMediaList(BaseModel):
    data: List[InstagramMedia]


def validate_json_types(
    json_obj: dict,
    json_type: Type[
        Union[
            ShortLivedAccessToken,
            LongLivedAccessToken,
            InstagramUserProfile,
            InstagramMedia,
            InstagramMediaList,
        ]
    ],
    logging_info_extra: dict = {},
):
    try:
        json_type(**json_obj)
    except ValidationError as e:
        logger.error(
            f"JSON Decode Error: {json_obj}",
            extra=logging_info_extra,
            exc_info=e,
        )
        return False
    return True
