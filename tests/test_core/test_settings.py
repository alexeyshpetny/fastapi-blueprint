from src.core.settings import settings


def test_testing_flag_is_enabled() -> None:
    assert settings.TESTING is True, "TESTING flag should be True during tests"
