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
    upload_max_bytes: int = 10 * 1024 * 1024
    worker_poll_seconds: float = 0.25
    media_ticket_ttl_seconds: int = Field(900, ge=60, le=3600)

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

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
        database_url = self.resolved_database_url
        if not database_url.startswith("mysql+pymysql://"):
            raise ValueError("云环境数据库必须使用 mysql+pymysql")


@lru_cache
def get_settings() -> Settings:
    return Settings()
