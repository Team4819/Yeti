import pytest
from os import path

@pytest.fixture(scope="function")
def yeti():
    import yeti
    return yeti

@pytest.fixture(scope="function")
def context(yeti):
    return yeti.Context()

@pytest.fixture(scope="function")
def resources_dir():
    return path.join(path.dirname(path.realpath(__file__)), "resources")