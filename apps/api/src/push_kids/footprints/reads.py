"""Owner-side bounded projections. Counts aggregate in SQL; no client album aggregation."""

from datetime import date, datetime

from sqlalchemy import case, func, or_, select, tuple_, union_all

from push_kids.footprints import access
from push_kids.footprints.models import FootprintPhoto as Photo
from push_kids.footprints.models import FootprintScope
from push_kids.footprints.models import FootprintVisit as Visit
from push_kids.footprints.service import FootprintsService, view
from push_kids.platform.errors import ConflictError, NotFoundError
from push_kids.platform.pagination import decode_cursor, encode_cursor
from push_kids.platform.time import utcnow


def filters(family, child_id, start=None, end=None, place=None):
    result = [Visit.family_id == family, Visit.child_id == child_id]
    if start:
        result.append(Visit.local_date >= start)
    if end:
        result.append(Visit.local_date <= end)
    if start and end and start > end:
        raise ValueError("开始日期不能晚于结束日期")
    if place:
        result.append(Visit.place_key == place)
    return result


def _revision(db, family, child_id):
    return (
        db.scalar(
            select(FootprintScope.revision).where(
                FootprintScope.family_id == family,
                FootprintScope.child_id == child_id,
            )
        )
        or 0
    )


def _cursor_scope(family, child_id, kind, start, end, revision, extra=None):
    return ["footprint-v1", family, child_id, kind, start, end, revision, extra]


def _visit_view(row):
    return {
        "id": row.id,
        "local_date": row.local_date.isoformat(),
        "local_time": row.sort_time if row.sort_time != "24:00:00" else None,
        "day_order": row.day_order,
        "place_key": row.place_key,
        "place_name": row.place_name,
        "city": row.city,
        "country": row.country,
        "latitude": row.latitude,
        "longitude": row.longitude,
        "coordinate_system": row.coordinate_system,
        "precision": row.precision,
    }


class FootprintReads:
    @staticmethod
    def drafts(db, family, child_id, cursor=None, limit=20):
        access.guard(db, family, child_id)
        revision = _revision(db, family, child_id)
        scope = _cursor_scope(family, child_id, "drafts", None, None, revision)
        now = utcnow()
        query = select(Photo).where(
            Photo.family_id == family,
            Photo.child_id == child_id,
            Photo.state.not_in(["confirmed", "expired", "deleted", "cancelled"]),
            or_(
                Photo.draft_expires_at > now,
                Photo.draft_expires_at.is_(None) & (Photo.ticket_expires_at > now),
            ),
        )
        if cursor:
            anchor = decode_cursor(cursor, scope)
            query = query.where(Photo.id > str(anchor["id"]))
        rows = list(db.scalars(query.order_by(Photo.id).limit(limit + 1)))
        more = len(rows) > limit
        rows = rows[:limit]
        return {
            "items": [view(row) for row in rows],
            "revision": revision,
            "next_cursor": encode_cursor(scope, {"id": rows[-1].id}) if more else None,
            "pending_count": FootprintsService.pending_count(db, family, child_id),
        }

    @staticmethod
    def visits(db, family, child_id, start=None, end=None, cursor=None, limit=20, place=None):
        access.guard(db, family, child_id)
        revision = _revision(db, family, child_id)
        scope = _cursor_scope(family, child_id, "visits", start, end, revision, place)
        query = select(Visit).where(*filters(family, child_id, start, end, place))
        if cursor:
            anchor = decode_cursor(cursor, scope)
            day, last_id = date.fromisoformat(anchor["date"]), str(anchor["id"])
            query = query.where(
                or_(Visit.local_date < day, (Visit.local_date == day) & (Visit.id < last_id))
            )
        rows = list(
            db.scalars(query.order_by(Visit.local_date.desc(), Visit.id.desc()).limit(limit + 1))
        )
        more, rows = len(rows) > limit, rows[:limit]
        ids = [row.id for row in rows]
        counts = (
            dict(
                db.execute(
                    select(Photo.visit_id, func.sum(case((Photo.is_manual.is_(False), 1), else_=0)))
                    .where(
                        Photo.family_id == family,
                        Photo.child_id == child_id,
                        Photo.state == "confirmed",
                        Photo.visit_id.in_(ids),
                    )
                    .group_by(Photo.visit_id)
                ).all()
            )
            if ids
            else {}
        )
        # Each index range reads four entries. A single UNION query remains bounded on
        # MySQL 5.7/SQLite even when one visit contains tens of thousands of photos.
        tops = [
            select(Photo.id)
            .where(
                Photo.family_id == family,
                Photo.child_id == child_id,
                Photo.visit_id == visit_id,
                Photo.state == "confirmed",
            )
            .order_by(Photo.ordinal, Photo.id)
            .limit(4)
            .subquery()
            for visit_id in ids
        ]
        # Materialize once before joining. MySQL 5.7 turns IN(UNION ...) into a
        # dependent subquery and may repeat every branch for each family photo.
        top_ids = union_all(*(select(top.c.id) for top in tops)).subquery() if tops else None
        previews = (
            list(
                db.scalars(
                    select(Photo)
                    .join(top_ids, Photo.id == top_ids.c.id)
                    .where(
                        Photo.family_id == family,
                        Photo.child_id == child_id,
                        Photo.state == "confirmed",
                    )
                    .order_by(Photo.ordinal, Photo.id)
                )
            )
            if ids
            else []
        )
        by_visit: dict = {}
        for photo in previews:
            by_visit.setdefault(photo.visit_id, []).append(view(photo))
        return {
            "items": [
                {
                    **_visit_view(row),
                    "photo_count": counts.get(row.id, 0),
                    "photos": by_visit.get(row.id, []),
                }
                for row in rows
            ],
            "revision": revision,
            "next_cursor": encode_cursor(
                scope, {"date": rows[-1].local_date.isoformat(), "id": rows[-1].id}
            )
            if more
            else None,
        }

    @staticmethod
    def photos(db, family, child_id, visit_id, cursor=None, limit=20):
        access.guard(db, family, child_id)
        revision = _revision(db, family, child_id)
        scope = _cursor_scope(family, child_id, "photos", None, None, revision, visit_id)
        visit = db.scalar(
            select(Visit).where(
                Visit.family_id == family, Visit.child_id == child_id, Visit.id == visit_id
            )
        )
        if not visit:
            raise NotFoundError("没有找到这次到访")
        query = select(Photo).where(
            Photo.family_id == family,
            Photo.child_id == child_id,
            Photo.visit_id == visit_id,
            Photo.state == "confirmed",
        )
        if cursor:
            anchor = decode_cursor(cursor, scope)
            query = query.where(Photo.id > str(anchor["id"]))
        rows = list(db.scalars(query.order_by(Photo.id).limit(limit + 1)))
        more, rows = len(rows) > limit, rows[:limit]
        return {
            "items": [
                {**view(row), "day_order": visit.day_order, "order_revision": revision}
                for row in rows
            ],
            "revision": revision,
            "next_cursor": encode_cursor(scope, {"id": rows[-1].id}) if more else None,
        }

    @staticmethod
    def summary(db, family, child_id, start=None, end=None):
        access.guard(db, family, child_id)
        scope = filters(family, child_id, start, end)
        values = db.execute(
            select(func.count(), func.count(func.distinct(Visit.country))).where(*scope)
        ).one()
        place_count = (
            db.scalar(
                select(func.count(func.distinct(Visit.place_key))).where(
                    *scope, or_(Visit.place_name.is_not(None), Visit.latitude.is_not(None))
                )
            )
            or 0
        )
        cities = (
            select(Visit.country, Visit.city)
            .where(*scope, Visit.city.is_not(None))
            .group_by(Visit.country, Visit.city)
            .subquery()
        )
        photo_count = (
            db.scalar(
                select(func.count())
                .select_from(Photo)
                .join(Visit, Photo.visit_id == Visit.id)
                .where(
                    *scope,
                    Photo.family_id == family,
                    Photo.child_id == child_id,
                    Photo.state == "confirmed",
                    Photo.is_manual.is_(False),
                )
            )
            or 0
        )
        missing = (
            db.scalar(
                select(func.count())
                .select_from(Photo)
                .join(Visit)
                .where(
                    *scope,
                    Photo.family_id == family,
                    Photo.child_id == child_id,
                    Photo.state == "confirmed",
                    Photo.is_manual.is_(False),
                    Visit.latitude.is_(None),
                )
            )
            or 0
        )
        return {
            "visit_days": values[0],
            "places": place_count,
            "countries": values[1],
            "cities": db.scalar(select(func.count()).select_from(cities)) or 0,
            "photos": photo_count,
            "unlocated_photos": missing,
            "drafts": FootprintsService.pending_count(db, family, child_id),
            "revision": _revision(db, family, child_id),
        }

    @staticmethod
    def map_points(db, family, child_id, start=None, end=None, bounds=None, mode="auto"):
        access.guard(db, family, child_id)
        criteria = filters(family, child_id, start, end)
        located = [*criteria, Visit.latitude.is_not(None), Visit.coordinate_system == "gcj02"]
        # A raw WGS84 point is never silently rendered as a domestic GCJ02 point.
        waiting = (
            db.scalar(
                select(func.count())
                .select_from(Visit)
                .where(*criteria, Visit.latitude.is_not(None), Visit.coordinate_system != "gcj02")
            )
            or 0
        )
        if mode == "world":
            west, south, east, north = -180.0, -90.0, 180.0, 90.0
        elif bounds:
            west, south, east, north = bounds
        elif mode == "china":
            west, south, east, north = 73.0, 18.0, 136.0, 54.0
        else:
            # Concentration wins over a lone distant visit, even within a large country.
            band_x = func.floor((Visit.longitude + 180) / 30)
            band_y = func.floor((Visit.latitude + 90) / 30)
            region = db.execute(
                select(band_x, band_y)
                .where(*located)
                .group_by(band_x, band_y)
                .order_by(func.count().desc(), band_x, band_y)
                .limit(1)
            ).first()
            box = db.execute(
                select(
                    func.min(Visit.longitude),
                    func.min(Visit.latitude),
                    func.max(Visit.longitude),
                    func.max(Visit.latitude),
                ).where(
                    *located,
                    band_x == (region[0] if region else -1),
                    band_y == (region[1] if region else -1),
                )
            ).one()
            if box[0] is None:
                west, south, east, north = 73.0, 18.0, 136.0, 54.0
            else:
                pad_x, pad_y = (
                    max((box[2] - box[0]) * 0.12, 0.04),
                    max((box[3] - box[1]) * 0.12, 0.04),
                )
                west, south, east, north = (
                    max(-180, box[0] - pad_x),
                    max(-90, box[1] - pad_y),
                    min(180, box[2] + pad_x),
                    min(90, box[3] + pad_y),
                )
        if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
            raise ValueError("地图范围无效")
        inside = [
            *located,
            Visit.longitude.between(west, east),
            Visit.latitude.between(south, north),
        ]
        x = case(
            (Visit.longitude >= east, 12),
            else_=func.floor((Visit.longitude - west) / max((east - west) / 13, 0.000001)),
        )
        y = case(
            (Visit.latitude >= north, 11),
            else_=func.floor((Visit.latitude - south) / max((north - south) / 12, 0.000001)),
        )
        rows = db.execute(
            select(
                x.label("x"),
                y.label("y"),
                func.avg(Visit.latitude),
                func.avg(Visit.longitude),
                func.count(),
                func.min(Visit.place_key),
                func.min(Visit.place_name),
                func.count(func.distinct(Visit.place_key)),
            )
            .where(*inside)
            .group_by(x, y)
            .order_by(x, y)
            .limit(200)
        ).all()
        total = db.scalar(select(func.count()).select_from(Visit).where(*located)) or 0
        shown = sum(row[4] for row in rows)
        return {
            "items": [
                {
                    "id": index + 1,
                    "latitude": row[2],
                    "longitude": row[3],
                    "visit_days": row[4],
                    "place_key": row[5] if row[7] == 1 else None,
                    "label": row[6] if row[7] == 1 else f"{row[4]}个到访日",
                    "bounds": [
                        max(west, west + row[0] * (east - west) / 13),
                        max(south, south + row[1] * (north - south) / 12),
                        min(east, west + (row[0] + 1) * (east - west) / 13),
                        min(north, south + (row[1] + 1) * (north - south) / 12),
                    ],
                }
                for index, row in enumerate(rows)
            ],
            "bounds": [west, south, east, north],
            "outside_visit_days": total - shown,
            "needs_conversion": waiting,
            "revision": _revision(db, family, child_id),
        }

    @staticmethod
    def playback(db, family, child_id, start=None, end=None, cursor=None, expected_revision=None):
        access.guard(db, family, child_id)
        revision = _revision(db, family, child_id)
        if expected_revision is not None and expected_revision != revision:
            raise ConflictError("足迹已更新，请重新开始回放")
        criteria = filters(family, child_id, start, end)
        waiting = (
            db.scalar(
                select(func.count())
                .select_from(Visit)
                .where(*criteria, Visit.latitude.is_not(None), Visit.coordinate_system != "gcj02")
            )
            or 0
        )
        scope = _cursor_scope(family, child_id, "playback", start, end, revision)
        query = select(Visit).where(
            *criteria, Visit.latitude.is_not(None), Visit.coordinate_system == "gcj02"
        )
        if cursor:
            anchor = decode_cursor(cursor, scope)
            query = query.where(
                tuple_(
                    Visit.local_date,
                    Visit.day_order,
                    Visit.sort_time,
                    Visit.sort_created_at,
                    Visit.id,
                )
                > tuple_(
                    date.fromisoformat(anchor["date"]),
                    int(anchor["order"]),
                    str(anchor["time"]),
                    datetime.fromisoformat(anchor["created"]),
                    str(anchor["id"]),
                )
            )
        rows = list(
            db.scalars(
                query.order_by(
                    Visit.local_date,
                    Visit.day_order,
                    Visit.sort_time,
                    Visit.sort_created_at,
                    Visit.id,
                ).limit(101)
            )
        )
        more, rows = len(rows) > 100, rows[:100]
        return {
            "items": [_visit_view(row) for row in rows],
            "needs_conversion": waiting,
            "revision": revision,
            "next_cursor": encode_cursor(
                scope,
                {
                    "date": rows[-1].local_date.isoformat(),
                    "order": rows[-1].day_order,
                    "time": rows[-1].sort_time,
                    "created": rows[-1].sort_created_at.isoformat(),
                    "id": rows[-1].id,
                },
            )
            if more
            else None,
            "order_note": "按照片当地日期及到访顺序播放，连线仅为顺序示意",
        }
