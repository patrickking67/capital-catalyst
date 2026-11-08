import pytest

from app import DEFAULT_DATABASE_URL, create_app, load_config


def test_missing_secret_key_is_refused(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY is not set"):
        create_app()


def test_config_reads_environment(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "env-value-for-test")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///other.db")
    config = load_config()
    assert config["SECRET_KEY"] == "env-value-for-test"
    assert config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///other.db"


def test_database_url_has_local_default(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "env-value-for-test")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert load_config()["SQLALCHEMY_DATABASE_URI"] == DEFAULT_DATABASE_URL


def test_testing_mode_does_not_need_a_secret(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    assert load_config({"TESTING": True})["TESTING"] is True


def test_init_db_command_creates_tables(app):
    result = app.test_cli_runner().invoke(args=["init-db"])
    assert result.exit_code == 0
    assert "Database tables created." in result.output
