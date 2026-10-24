"""Fixed Tencent adapter: optional metadata enrichment and parent-confirmable search."""

import json
from urllib.parse import urlencode
from urllib.request import urlopen

from push_kids.footprints.schemas import Place
from push_kids.platform.errors import DependencyError


class TencentPlaces:
    def __init__(self, key: str | None):
        self.key = key

    def _get(self, path, params):
        if not self.key:
            return None
        url = "https://apis.map.qq.com" + path + "?" + urlencode({**params, "key": self.key})
        try:
            with urlopen(url, timeout=8) as response:  # noqa: S310 - fixed Tencent host
                raw = response.read(256 * 1024 + 1)
            if len(raw) > 256 * 1024:
                raise ValueError
            result = json.loads(raw)
            if result.get("status") != 0:
                raise ValueError
            return result
        except Exception as exc:
            raise DependencyError("地点服务暂时不可用，可手动填写") from exc

    def reverse(self, latitude, longitude):
        result = self._get(
            "/ws/geocoder/v1/",
            {
                "location": f"{latitude},{longitude}",
                "coord_type": 1,
                "get_poi": 0,
            },
        )
        if not result:
            return None
        address = result.get("result", {}).get("address_component", {})
        return Place(
            place_name=address.get("city") or address.get("nation"),
            city=address.get("city") or None,
            country=address.get("nation") or None,
            precision="city",
        )

    def convert(self, latitude, longitude):
        result = self._get(
            "/ws/coord/v1/translate",
            {
                "locations": f"{latitude},{longitude}",
                "type": 1,
            },
        )
        if not result:
            return None
        locations = result.get("locations") or []
        if not locations:
            return None
        return Place(
            latitude=locations[0].get("lat"),
            longitude=locations[0].get("lng"),
            coordinate_system="gcj02",
            precision="poi",
        )

    def search(self, keyword: str, region: str):
        result = self._get(
            "/ws/place/v1/search",
            {
                "keyword": keyword,
                "boundary": f"region({region},0)",
                "page_size": 3,
            },
        )
        if not result:
            return []
        candidates = []
        for item in result.get("data", [])[:3]:
            address = item.get("ad_info") or {}
            location = item.get("location") or {}
            candidates.append(
                Place(
                    place_name=item.get("title"),
                    city=address.get("city"),
                    country=address.get("nation"),
                    latitude=location.get("lat"),
                    longitude=location.get("lng"),
                    coordinate_system="gcj02",
                    precision="poi",
                )
            )
        return candidates
