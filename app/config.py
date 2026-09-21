"""应用配置：路径、数据库与模型服务设置，全部从环境变量读取一次。

配置集中在这里的好处：测试可以构造一份自己的 Settings（例如把数据库换成内存库），
而不用去改模块级全局变量。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str
    model: str
    request_timeout: float
    db_path: str
    taxonomy_path: Path
    schema_path: Path
    web_dir: Path
    app_version: str

    @property
    def model_configured(self) -> bool:
        """是否配置了可用的模型密钥；未配置时系统降级为纯手工流程。"""
        return bool(self.api_key) and self.api_key != 'your_api_key_here'

    def with_db(self, path) -> 'Settings':
        return replace(self, db_path=str(path))


def load_settings() -> Settings:
    return Settings(
        api_key=os.getenv('DEEPSEEK_API_KEY', ''),
        base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
        model=os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
        request_timeout=float(os.getenv('DEEPSEEK_TIMEOUT', '35')),
        db_path=os.getenv('CODEPOWERPLUS_DB_PATH') or str(ROOT / 'data' / 'codepowerplus.db'),
        taxonomy_path=ROOT / 'data' / 'knowledge_taxonomy.json',
        schema_path=ROOT / 'data' / 'knowledge_taxonomy.schema.json',
        web_dir=ROOT / 'app' / 'static',
        app_version='0.3.0',
    )


settings = load_settings()
