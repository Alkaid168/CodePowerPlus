"""配置：默认路径、派生路径与模型开关。"""
from dataclasses import replace

from app.config import ROOT, load_settings


def test_local_defaults():
    settings = load_settings()
    assert settings.model and settings.base_url.startswith('http')
    assert settings.request_timeout > 0
    assert settings.taxonomy_path == ROOT / 'data' / 'knowledge_taxonomy.json'
    assert settings.schema_path == ROOT / 'data' / 'knowledge_taxonomy.schema.json'
    assert settings.web_dir == ROOT / 'app' / 'static'
    assert settings.app_version


def test_with_db_and_model_flag():
    settings = load_settings()
    assert settings.with_db(':memory:').db_path == ':memory:'
    assert replace(settings, api_key='').model_configured is False
    assert replace(settings, api_key='your_api_key_here').model_configured is False
    assert replace(settings, api_key='sk-real').model_configured is True
