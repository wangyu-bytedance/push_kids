import json
import re
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_CONTAINER_PORT = 8000


def test_non_root_container_uses_consistent_unprivileged_port() -> None:
    dockerfile = (REPOSITORY_ROOT / "Dockerfile").read_text()
    compose = (REPOSITORY_ROOT / "docker-compose.yml").read_text()
    service_settings = json.loads(
        (REPOSITORY_ROOT / "deploy/cloudbase/service-settings.json").read_text()
    )
    wxcloud_settings = json.loads((REPOSITORY_ROOT / "wxcloud.config.json").read_text())

    user_match = re.search(r"^USER\s+(\d+)\s*$", dockerfile, re.MULTILINE)
    assert user_match is not None
    assert int(user_match.group(1)) != 0

    exposed_port_match = re.search(r"^EXPOSE\s+(\d+)\s*$", dockerfile, re.MULTILINE)
    assert exposed_port_match is not None
    exposed_port = int(exposed_port_match.group(1))
    assert exposed_port == EXPECTED_CONTAINER_PORT
    assert exposed_port >= 1024
    assert "${PORT:-8000}" in dockerfile

    assert service_settings["containerPort"] == EXPECTED_CONTAINER_PORT
    assert wxcloud_settings["server"]["port"] == EXPECTED_CONTAINER_PORT
    assert '"8000:8000"' in compose
    assert "http://127.0.0.1:8000/health/ready" in compose
