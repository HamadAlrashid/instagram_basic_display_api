from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func, TEXT, JSON
from pgvector.sqlalchemy import Vector
from typing import List, Optional
from sqlalchemy.orm import mapped_column, Mapped
from models.types.instagram_media_type import InstagramMediaType
from sqlalchemy import UniqueConstraint


class InstagramMedia():
    __tablename__ = "instagram_media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    __table_args__ = (UniqueConstraint("media_id", "user_id", name="media_user_uc"),)

    # user_id = 

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Data retrieved from Instagram API
    media_id: Mapped[str] = mapped_column(String(255), nullable=False)
    publish_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    media_type: Mapped[InstagramMediaType] = mapped_column(String(255), nullable=False)
    media_url: Mapped[str] = mapped_column(TEXT, nullable=False)
    permalink: Mapped[str] = mapped_column(TEXT, nullable=True)
    thumbnail_url: Mapped[str] = mapped_column(TEXT, nullable=True)
    caption: Mapped[str] = mapped_column(TEXT, nullable=True)
    album_children: Mapped[dict] = mapped_column(JSON, nullable=True)  # id:media_id

    # Data extracted from media
    parent_media_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    media_description: Mapped[str] = mapped_column(TEXT, nullable=True)
    embeddings: Mapped[Optional[List[float]]] = mapped_column(Vector(1536))
