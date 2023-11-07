import hashlib
import shutil
from pathlib import Path

import pytest

from isimip_qa.main import init_settings


def pytest_addoption(parser):
    parser.addoption('--init-files', dest='init_files', action='store_true', default=False)


@pytest.fixture(scope='session')
def config(pytestconfig):
    class Config:
        init_files = pytestconfig.getoption('init_files')

    return Config


@pytest.fixture(scope='session')
def settings(config):
    if config.init_files:
        extractions_path = Path('testing') / 'extractions'
        plots_path = Path('testing') / 'plots'
    else:
        extractions_path = plots_path = Path('testing') / 'tmp'

    shutil.rmtree(extractions_path, ignore_errors=True)
    shutil.rmtree(plots_path, ignore_errors=True)

    return init_settings(
        datasets_path=Path('testing') / 'datasets',
        extractions_path=extractions_path,
        plots_path=plots_path,
        plots_format='png'
    )


@pytest.fixture()
def checksum():
    def sha1_checksum(file_path):
        h = hashlib.sha1()
        with open(file_path, 'rb') as fp:
            h.update(fp.read())
        return h.hexdigest()

    return sha1_checksum
