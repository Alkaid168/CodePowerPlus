from app.config import settings

def test_config_has_safe_defaults():
    assert settings.model
    assert settings.base_url.startswith("http")
