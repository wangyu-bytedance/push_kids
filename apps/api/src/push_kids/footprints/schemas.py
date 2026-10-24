from datetime import date, datetime, time
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator, model_validator

ShortName = Annotated[str, Field(min_length=1, max_length=120)]


class Command(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, allow_inf_nan=False)


class ImportCreate(Command):
    child_id: str = Field(min_length=1, max_length=36)
    count: int = Field(ge=1, le=20, strict=True)
    consented: Literal[True]


class PreferencePatch(Command):
    ai_enabled: StrictBool
    consented: Literal[True]


class Place(Command):
    place_name: ShortName | None = None
    city: str | None = Field(None, max_length=80)
    country: str | None = Field(None, max_length=80)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    coordinate_system: Literal["wgs84", "gcj02"] | None = None
    precision: Literal["poi", "city", "unknown"] = "unknown"

    @model_validator(mode="after")
    def coordinates(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("经纬度需要一起填写或清除")
        if self.latitude is not None and not self.coordinate_system:
            raise ValueError("请明确坐标来源")
        if self.latitude is None:
            object.__setattr__(self, "coordinate_system", None)
        return self


class PhotoPatch(Place):
    version: int = Field(ge=0, strict=True)
    local_date: date | None = None
    local_time: str | None = None
    offset_minutes: int | None = Field(None, ge=-720, le=840, strict=True)
    day_order: int | None = Field(None, ge=-100000, le=100000, strict=True)
    order_revision: int | None = Field(None, ge=0, strict=True)

    @field_validator("local_time")
    @classmethod
    def validate_time(cls, value):
        if value is not None:
            parsed = time.fromisoformat(value)
            if parsed.tzinfo or len(value) not in (5, 8):
                raise ValueError("请填写当地时刻，不要补造时区")
            return parsed.isoformat()
        return None


class PhotoVersion(Command):
    id: str = Field(min_length=1, max_length=36)
    version: int = Field(ge=0, strict=True)


class ManualCreate(PhotoPatch):
    child_id: str = Field(min_length=1, max_length=36)
    local_date: date
    version: Literal[0] = 0

    @model_validator(mode="after")
    def no_formal_order(self):
        if self.day_order is not None or self.order_revision is not None:
            raise ValueError("手动草稿请先入档，再调整同日顺序")
        return self


class Confirm(Command):
    photos: list[PhotoVersion] = Field(min_length=1, max_length=20)
    confirm_actual_visit: Literal[True]

    @model_validator(mode="after")
    def unique_photos(self):
        if len({p.id for p in self.photos}) != len(self.photos):
            raise ValueError("同一照片只能选择一次")
        return self


class Claim(Command):
    file_id: str = Field(min_length=1, max_length=800)


class VisitOrder(Command):
    revision: int = Field(ge=0, strict=True)
    day_order: int = Field(ge=-100000, le=100000, strict=True)


class PhotoView(Place):
    model_config = ConfigDict(from_attributes=True)
    id: str
    import_id: str
    child_id: str
    version: int
    state: str
    job_state: str
    error_code: str | None
    local_date: date | None
    local_time: str | None
    offset_minutes: int | None
    occurred_at: datetime | None
    time_source: str
    location_source: str
    received_at: datetime | None
    draft_expires_at: datetime | None
    confirmed_at: datetime | None
    has_display: bool = False
    is_manual: bool
    duplicate_of: str | None
    candidates: list[Place] = Field(default_factory=list, max_length=3)
