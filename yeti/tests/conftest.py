import pytest


@pytest.fixture(scope="function")
def yeti():
    import yeti
    return yeti
