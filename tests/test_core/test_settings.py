from src.core.settings import settings


def test_environment_is_testing() -> None:
    assert settings.ENVIRONMENT == "testing", "ENVIRONMENT should be 'testing' during tests"
