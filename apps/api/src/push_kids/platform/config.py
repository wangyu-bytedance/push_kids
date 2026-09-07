from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = Field("development", alias="PUSH_KIDS_ENV")
    database_url: str | None = Field(None, alias="PUSH_KIDS_DATABASE_URL")
    mysql_address: str | None = Field(None, alias="MYSQL_ADDRESS")
    mysql_username: str | None = Field(None, alias="MYSQL_USERNAME")
    mysql_password: SecretStr | None = Field(None, alias="MYSQL_PASSWORD")
    mysql_database: str | None = Field(None, alias="MYSQL_DATABASE")
    media_root: Path = Field(Path("./uploads"), alias="PUSH_KIDS_MEDIA_ROOT")
    media_backend: Literal["local", "wechat_cloud"] = Field(
        "local", alias="PUSH_KIDS_MEDIA_BACKEND"
    )
    wechat_env_id: str | None = Field(None, alias="CBR_ENV_ID")
    wechat_expected_app_id: str | None = Field(None, alias="WECHAT_APP_ID")
    wechat_service_name: str = Field("flask-ik19", alias="WECHAT_SERVICE_NAME")
    wechat_storage_bucket: str | None = Field(
        None,
        validation_alias=AliasChoices("COS_BUCKET", "WECHAT_STORAGE_BUCKET"),
    )
    wechat_storage_region: str = Field(
        "ap-shanghai",
        validation_alias=AliasChoices("COS_REGION", "WECHAT_STORAGE_REGION"),
    )
    actor_hmac_key: SecretStr | None = Field(None, alias="PUSH_KIDS_ACTOR_HMAC_KEY")
    ai_provider: Literal["ark", "test"] = Field("ark", alias="PUSH_KIDS_AI_PROVIDER")
    run_worker: bool = Field(True, alias="PUSH_KIDS_RUN_WORKER")
    cors_origins: str = Field("", alias="PUSH_KIDS_CORS_ORIGINS")
    ark_api_key: SecretStr | None = Field(None, alias="ARK_API_KEY")
    ark_base_url: str = Field("https://ark.cn-beijing.volces.com/api/v3", alias="ARK_BASE_URL")
    ark_model: str = Field("doubao-seed-2-1-pro-260628", alias="ARK_MODEL")
    # Notifications stay off until a deployment supplies a real template map and key, so no
    # environment can accidentally promise WeChat reminders it cannot deliver.
    notification_channel: Literal["disabled", "recording", "wechat"] = Field(
        "disabled", alias="PUSH_KIDS_NOTIFICATION_CHANNEL"
    )
    notification_secret_key: SecretStr | None = Field(
        None, alias="PUSH_KIDS_NOTIFICATION_SECRET_KEY"
    )
    notification_templates: str = Field("", alias="PUSH_KIDS_NOTIFICATION_TEMPLATES")
    notification_trigger_token: SecretStr | None = Field(
        None, alias="PUSH_KIDS_NOTIFICATION_TRIGGER_TOKEN"
    )
    # Token configured in 微信后台「开发管理 → 消息推送」. Without it the inbound event route stays
    # absent, so an unconfigured deployment cannot be fed forged subscription events.
    wechat_message_token: SecretStr | None = Field(None, alias="PUSH_KIDS_WECHAT_MESSAGE_TOKEN")
    run_notification_scheduler: bool = Field(True, alias="PUSH_KIDS_RUN_NOTIFICATION_SCHEDULER")
    upload_max_bytes: int = 10 * 1024 * 1024
    worker_poll_seconds: float = 0.25
    notification_tick_seconds: float = Field(30.0, ge=1.0, le=300.0)
    media_ticket_ttl_seconds: int = Field(900, ge=60, le=3600)

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def notification_secret_value(self) -> str:
        """Plain secret for the destination cipher. Empty means "no external channel"."""
        if not self.notification_secret_key:
            return ""
        return self.notification_secret_key.get_secret_value().strip()

    @property
    def notification_trigger_value(self) -> str:
        if not self.notification_trigger_token:
            return ""
        return self.notification_trigger_token.get_secret_value().strip()

    @property
    def wechat_message_token_value(self) -> str:
        """Shared token for inbound WeChat message push. Empty means "route disabled"."""
        if not self.wechat_message_token:
            return ""
        return self.wechat_message_token.get_secret_value().strip()

    @property
    def is_cloud(self) -> bool:
        return self.env == "cloud"

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        if not self.is_cloud:
            return "sqlite:///./data/push_kids.db"
        missing = [
            name
            for name, value in (
                ("MYSQL_ADDRESS", self.mysql_address),
                ("MYSQL_USERNAME", self.mysql_username),
                ("MYSQL_PASSWORD", self.mysql_password),
                ("MYSQL_DATABASE", self.mysql_database),
            )
            if not value
        ]
        if missing:
            raise ValueError(f"云环境缺少数据库配置：{', '.join(missing)}")
        assert self.mysql_address and self.mysql_username and self.mysql_password
        assert self.mysql_database
        username = quote_plus(self.mysql_username)
        password = quote_plus(self.mysql_password.get_secret_value())
        database = quote_plus(self.mysql_database)
        return (
            f"mysql+pymysql://{username}:{password}@{self.mysql_address}/{database}?charset=utf8mb4"
        )

    def validate_cloud_runtime(self) -> None:
        if not self.is_cloud:
            return
        if not self.actor_hmac_key or len(self.actor_hmac_key.get_secret_value()) < 32:
            raise ValueError("云环境 PUSH_KIDS_ACTOR_HMAC_KEY 至少需要 32 个字符")
        if not self.wechat_env_id:
            raise ValueError("云托管运行环境缺少平台内置的 CBR_ENV_ID")
        if not self.wechat_expected_app_id:
            raise ValueError("云环境必须配置 WECHAT_APP_ID")
        if self.media_backend != "wechat_cloud":
            raise ValueError("云环境必须使用 PUSH_KIDS_MEDIA_BACKEND=wechat_cloud")
        if not self.wechat_storage_bucket:
            raise ValueError("云环境必须提供云托管注入的 COS_BUCKET")
        if not self.run_worker:
            raise ValueError("当前单实例 staging 必须启用 PUSH_KIDS_RUN_WORKER")
        if self.ai_provider == "ark" and (
            not self.ark_api_key or not self.ark_api_key.get_secret_value().strip()
        ):
            raise ValueError("云环境使用 Ark 时必须配置 ARK_API_KEY")
        if self.notification_channel == "recording":
            raise ValueError("云环境不能使用 recording 通知通道")
        if self.notification_channel == "wechat":
            if len(self.notification_secret_value) < 32:
                raise ValueError("开启微信提醒时 PUSH_KIDS_NOTIFICATION_SECRET_KEY 至少 32 个字符")
            if not self.notification_templates.strip():
                raise ValueError("开启微信提醒时必须配置 PUSH_KIDS_NOTIFICATION_TEMPLATES")
            if not self.run_notification_scheduler and not self.notification_trigger_value:
                raise ValueError("关闭进程内调度时必须配置 PUSH_KIDS_NOTIFICATION_TRIGGER_TOKEN")
        database_url = self.resolved_database_url
        if not database_url.startswith("mysql+pymysql://"):
            raise ValueError("云环境数据库必须使用 mysql+pymysql")


@lru_cache
def get_settings() -> Settings:
    return Settings()
