from shared.config import Settings
import os

def test_settings_defaults():
    """Test that default settings are set correctly"""
    settings = Settings()
    assert settings.database_name == "basmati"
    assert settings.service_port == 8000
    assert settings.environment == "development"

def test_settings_env_override(monkeypatch):
    """Test that environment variables override defaults"""
    monkeypatch.setenv("SERVICE_PORT", "9000")
    monkeypatch.setenv("DATABASE_NAME", "test_db")
    
    # Re-instantiate to pick up env vars
    settings = Settings()
    assert settings.service_port == 9000
    assert settings.database_name == "test_db"
