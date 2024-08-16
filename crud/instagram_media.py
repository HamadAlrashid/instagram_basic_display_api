from typing import Optional
from sqlalchemy.orm import Session
from types.instagram_media_type import InstagramMediaType
from models.instagram_media import InstagramMedia


class InstagramMediaCrud():
    def __init__(self) -> None:
        super().__init__(InstagramMedia)

    def bulk_upsert_media(
        self,
        db: Session,
        db_objs: list[InstagramMedia],
        batch_size: int = 1000,
    ) -> int:
        """Bulk upsert a list of media. If the media already exists, update the existing record."""        
        # IMPLEMENT HERE

    def get_media_by_user_id_media_id(
        self, db: Session, user_id: str, media_id: str
    ) -> Optional[InstagramMedia]:
        return (
            db.query(InstagramMedia)
            .filter_by(user_id=user_id, media_id=media_id)
            .first()
        )

    def get_all_media_by_user_id_media_type_desc(
        self, db: Session, user_id: str, media_type: Optional[InstagramMediaType] = None
    ) -> list[InstagramMedia]:
        """Get all media by user_id and media_type in descending order of publish_timestamp, with most recent first. If media_type is not specified, return all types of media."""
        if media_type is None:
            return (
                db.query(InstagramMedia)
                .filter_by(user_id=user_id)
                .order_by(InstagramMedia.publish_timestamp.desc())
                .all()
            )
        else:
            return (
                db.query(InstagramMedia)
                .filter_by(user_id=user_id, media_type=media_type.name)
                .order_by(InstagramMedia.publish_timestamp.desc())
                .all()
            )

    def get_n_most_recent_media_by_user_id_media_type(
        self,
        db: Session,
        user_id: str,
        n: int = 1,
        media_type: Optional[InstagramMediaType] = None,
    ) -> list[InstagramMedia]:
        """Get n most recent media by user_id and media_type in descending order of publish_timestamp, with most recent first. If media_type is not specified, return all types of media."""

        if media_type is None:
            return (
                db.query(InstagramMedia)
                .filter_by(user_id=user_id)
                .order_by(InstagramMedia.publish_timestamp.desc())
                .limit(n)
                .all()
            )
        else:
            return (
                db.query(InstagramMedia)
                .filter_by(user_id=user_id, media_type=media_type.name)
                .order_by(InstagramMedia.publish_timestamp.desc())
                .limit(n)
                .all()
            )


