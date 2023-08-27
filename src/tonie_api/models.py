"""Dataclass models of all relevant TonieCloudAPI objects."""
from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    uuid: str
    email: str


class Config(BaseModel):
    locales: list[str]
    unicodeLocales: list[str]
    maxChapters: int
    maxSeconds: int
    maxBytes: int
    accepts: list[str]
    stageWarning: bool
    paypalClientId: str
    ssoEnabled: bool


class Household(BaseModel):
    id: str
    name: str
    ownerName: str
    access: str
    canLeave: bool


class Chapter(BaseModel):
    id: str  # 	ID of this chapter (for existing chapters)
    title: str  # Human-readable name for this chapter
    # File identifier. For new chapters: a UUID (see POST /file on how to generate it).
    # For existing chapters: an opaque blob(only used in case of concurrent editing by another device).
    # Starts with "ContentToken:" if this chapter is from a Content-Token,
    # followed by the content token followed by ":", followed by the 0-indexed chapter of the Content-Token.
    file: str
    seconds: float  # Length of this chapter in seconds
    transcoding: bool  # 	Is this chapter currently transcoding?


class CreativeTonie(BaseModel):
    id: str
    householdId: str
    name: str
    imageUrl: str
    secondsRemaining: float
    secondsPresent: float
    chaptersRemaining: int
    chaptersPresent: int
    transcoding: bool
    lastUpdate: None | datetime
    chapters: list[Chapter]


class Request(BaseModel):
    url: str
    fields: dict


class FileUploadRequest(BaseModel):
    request: Request
    fileId: str
