from models import InstagramMedia
from crud import instagram_media_crud
from models.types import InstagramMediaType
from datetime import datetime


TEST_ALBUM = {
    "caption": "My favorite two things",
    "id": "18024887825474332",
    "media_type": "CAROUSEL_ALBUM",
    "media_url": "https://scontent-yyz1-1.cdninstagram.com/v/t51.29350-15/448168320_1218738966239746_4250650015589670152_n.heic?stp=dst-jpg&_nc_cat=106&ccb=1-7&_nc_sid=18de74&_nc_ohc=FqEN413G7hsQ7kNvgEYdnby&_nc_ht=scontent-yyz1-1.cdninstagram.com&edm=ANo9K5cEAAAA&oh=00_AYDeefV7B8cpLxFupsWMpMCh5occ3TE5Dygb0ib1-bj7Sg&oe=6671498A",
    "permalink": "",
    "timestamp": "2024-06-11T21:09:24+0000",
    "username": "",
    "children": {"data": [{"id": "17993297984492797"}, {"id": "18035887075941921"}]},
}


TEST_VIDEO = {
    "id": "17857002054143388",
    "media_type": "VIDEO",
    "media_url": "https://scontent-yyz1-1.cdninstagram.com/o1/v/t16/f1/m82/A9463D89C214CE5E1DB8F241F70AC0A0_video_dashinit.mp4?efg=eyJ2ZW5jb2RlX3RhZyI6InZ0c192b2RfdXJsZ2VuLmNsaXBzLnVua25vd24tQzMuMzU4LmRhc2hfYmFzZWxpbmVfM192MSJ9&_nc_ht=scontent-yyz1-1.cdninstagram.com&_nc_cat=104&vs=829339358637369_3642606302&_nc_vs=HBksFQIYT2lnX3hwdl9yZWVsc19wZXJtYW5lbnRfcHJvZC9BOTQ2M0Q4OUMyMTRDRTVFMURCOEYyNDFGNzBBQzBBMF92aWRlb19kYXNoaW5pdC5tcDQVAALIAQAVAhg6cGFzc3Rocm91Z2hfZXZlcnN0b3JlL0dEQ0F0eHEtZnd3VlNhZ0JBQmxQV3YtZzJySXNicV9FQUFBRhUCAsgBACgAGAAbAYgHdXNlX29pbAExFQAAJpyL2tKY0qZAFQIoAkMzLBdAWAIcrAgxJxgSZGFzaF9iYXNlbGluZV8zX3YxEQB1AAA%3D&ccb=9-4&oh=00_AYDsrdXX_b7-mo-D5V_7QUBuju-iZuk9e-r4Pj_Irzz2Eg&oe=666D60DD&_nc_sid=1d576d",
    "permalink": "",
    "thumbnail_url": "https://scontent-yyz1-1.cdninstagram.com/v/t51.29350-15/448209063_2061207707606244_2637482582770153091_n.jpg?_nc_cat=108&ccb=1-7&_nc_sid=18de74&_nc_ohc=TLIQiNgpi5oQ7kNvgFdQYiF&_nc_ht=scontent-yyz1-1.cdninstagram.com&edm=ANo9K5cEAAAA&oh=00_AYAnJtzVaiXLYcLEuxIElepEqWe5oZ__0F_R-YJwbrxuSg&oe=66716569",
    "timestamp": "2024-06-11T21:03:37+0000",
    "username": "",
}


TEST_IMAGE = {
    "id": "18030813908042291",
    "media_type": "IMAGE",
    "media_url": "https://scontent-yyz1-1.cdninstagram.com/v/t51.29350-15/448120915_471134901993984_3894353649782464615_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=18de74&_nc_ohc=ZcL6GGr5qWMQ7kNvgHwX1DC&_nc_ht=scontent-yyz1-1.cdninstagram.com&edm=ANo9K5cEAAAA&oh=00_AYBRSXAkpkdhCwiR1QAWG3WCQPFqRHPRIQwOkgoeR6tRKQ&oe=66715A7B",
    "permalink": "",
    "timestamp": "2024-06-11T20:59:45+0000",
    "username": "",
}


def helper_construct_media_from_dict(
    media_dict,
    user_id="test_user_id",
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
        embeddings=media_dict.get("embeddings"),
    )


def test_get_media_by_user_id_media_id(mocked_session):
    instagram_media_crud.bulk_upsert_media(
        mocked_session,
        [
            helper_construct_media_from_dict(TEST_IMAGE),
        ],
    )

    fetched_instagram_user_media = instagram_media_crud.get_media_by_user_id_media_id(
        mocked_session, user_id="test_user_id", media_id=TEST_IMAGE["id"]
    )

    assert fetched_instagram_user_media is not None
    assert fetched_instagram_user_media.media_id == TEST_IMAGE["id"]
    assert fetched_instagram_user_media.publish_timestamp == datetime(
        2024, 6, 11, 20, 59, 45
    )
    assert fetched_instagram_user_media.media_type == InstagramMediaType.IMAGE.name
    assert fetched_instagram_user_media.media_url == TEST_IMAGE["media_url"]
    assert fetched_instagram_user_media.permalink == TEST_IMAGE["permalink"]

    assert fetched_instagram_user_media.media_description is None
    assert fetched_instagram_user_media.thumbnail_url is None
    assert fetched_instagram_user_media.caption is None
    assert fetched_instagram_user_media.album_children is None
    assert fetched_instagram_user_media.parent_media_id is None
    assert fetched_instagram_user_media.embeddings is None


def test_get_all_media_by_user_id_media_type_desc(mocked_session):
    instagram_media_crud.bulk_upsert_media(
        mocked_session,
        [helper_construct_media_from_dict(TEST_IMAGE)],
    )

    assert len(mocked_session.query(InstagramMedia).all()) == 1

    instagram_media_crud.bulk_upsert_media(
        mocked_session,
        [helper_construct_media_from_dict(TEST_VIDEO)],
    )

    assert len(mocked_session.query(InstagramMedia).all()) == 2

    # Test fetching all media types in descending order of publish_timestamp
    fetched_all_instagram_user_media = (
        instagram_media_crud.get_all_media_by_user_id_media_type_desc(
            mocked_session, user_id="test_user_id"
        )
    )

    assert len(fetched_all_instagram_user_media) == 2

    assert fetched_all_instagram_user_media[0].user_id == "test_user_id"
    assert fetched_all_instagram_user_media[0].media_id == TEST_VIDEO["id"]
    assert fetched_all_instagram_user_media[0].publish_timestamp == datetime(
        2024, 6, 11, 21, 3, 37
    )
    assert (
        fetched_all_instagram_user_media[0].media_type == InstagramMediaType.VIDEO.name
    )
    assert fetched_all_instagram_user_media[0].media_url == TEST_VIDEO["media_url"]
    assert fetched_all_instagram_user_media[0].permalink == TEST_VIDEO["permalink"]
    assert (
        fetched_all_instagram_user_media[0].thumbnail_url == TEST_VIDEO["thumbnail_url"]
    )

    assert fetched_all_instagram_user_media[1].user_id == "test_user_id"
    assert fetched_all_instagram_user_media[1].media_id == TEST_IMAGE["id"]
    assert fetched_all_instagram_user_media[1].publish_timestamp == datetime(
        2024, 6, 11, 20, 59, 45
    )
    assert (
        fetched_all_instagram_user_media[1].media_type == InstagramMediaType.IMAGE.name
    )
    assert fetched_all_instagram_user_media[1].media_url == TEST_IMAGE["media_url"]
    assert fetched_all_instagram_user_media[1].permalink == TEST_IMAGE["permalink"]

    # Test fetching only images
    fetched_only_image_instagram_user_media = (
        instagram_media_crud.get_all_media_by_user_id_media_type_desc(
            mocked_session, user_id="test_user_id", media_type=InstagramMediaType.IMAGE
        )
    )

    assert len(fetched_only_image_instagram_user_media) == 1
    assert (
        fetched_only_image_instagram_user_media[0].media_type
        == InstagramMediaType.IMAGE.name
    )

    # Test fetching only videos
    fetched_only_video_instagram_user_media = (
        instagram_media_crud.get_all_media_by_user_id_media_type_desc(
            mocked_session, user_id="test_user_id", media_type=InstagramMediaType.VIDEO
        )
    )

    assert len(fetched_only_video_instagram_user_media) == 1

    assert (
        fetched_only_video_instagram_user_media[0].media_type
        == InstagramMediaType.VIDEO.name
    )


def test_get_n_most_recent_media_by_user_id_media_type(mocked_session):
    instagram_media_crud.bulk_upsert_media(
        mocked_session,
        [
            helper_construct_media_from_dict(TEST_IMAGE),
        ],
    )

    assert len(mocked_session.query(InstagramMedia).all()) == 1

    instagram_media_crud.bulk_upsert_media(
        mocked_session,
        [
            helper_construct_media_from_dict(TEST_VIDEO),
        ],
    )

    assert len(mocked_session.query(InstagramMedia).all()) == 2

    # Testing fetching 1 most recent media
    fetched_most_recent_instagram_user_media = (
        instagram_media_crud.get_n_most_recent_media_by_user_id_media_type(
            mocked_session, user_id="test_user_id", n=1
        )
    )

    assert len(fetched_most_recent_instagram_user_media) == 1
    assert fetched_most_recent_instagram_user_media[0].media_id == TEST_VIDEO["id"]

    # Testing fetching 2 most recent media
    fetched_2_most_recent_instagram_user_media = (
        instagram_media_crud.get_n_most_recent_media_by_user_id_media_type(
            mocked_session, user_id="test_user_id", n=2
        )
    )

    assert len(fetched_2_most_recent_instagram_user_media) == 2
    assert fetched_2_most_recent_instagram_user_media[0].media_id == TEST_VIDEO["id"]
    assert fetched_2_most_recent_instagram_user_media[1].media_id == TEST_IMAGE["id"]


def test_fetch_non_existent(mocked_session):
    fetched_all_instagram_user_media = (
        instagram_media_crud.get_all_media_by_user_id_media_type_desc(
            mocked_session, user_id="DOES_NOT_EXIST"
        )
    )

    assert len(fetched_all_instagram_user_media) == 0

    fetched_non_existent_media_id = instagram_media_crud.get_media_by_user_id_media_id(
        mocked_session, user_id="DOES_NOT_EXIST", media_id="DOES_NOT_EXIST"
    )

    assert fetched_non_existent_media_id is None
