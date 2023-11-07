import pytest


def pytest_addoption(parser):
    parser.addoption('--init-files', dest='init_files', action='store_true', default=False)


@pytest.fixture(scope='session')
def config(pytestconfig):
    class Config:
        init_files = pytestconfig.getoption('init_files')

    return Config
