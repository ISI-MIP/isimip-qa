import filecmp
import shutil
from pathlib import Path

import pytest

from isimip_qa.extractions import extraction_classes
from isimip_qa.main import init_settings
from isimip_qa.models import Dataset

datasets = [
    'linear',
    'mask',
    'point',
    'sine'
]

@pytest.fixture(scope='module')
def settings(config):
    if config.init_files:
        extractions_path = Path('testing') / 'extractions'
    else:
        extractions_path = Path('testing') / 'tmp'

    shutil.rmtree(extractions_path, ignore_errors=True)

    return init_settings(
        datasets_path=Path('testing') / 'datasets',
        extractions_path=extractions_path
    )

@pytest.mark.parametrize('dataset_path', datasets)
@pytest.mark.parametrize('extraction_class', extraction_classes)
def test_extraction(config, settings, dataset_path, extraction_class):
    dataset = Dataset(dataset_path)
    extraction = extraction_class(dataset)
    extraction.path.unlink(missing_ok=True)

    for file in dataset.files:
        file.open()
        extraction.extract(file)
        file.close()

    assert extraction.path.exists()

    if not config.init_files:
        assert filecmp.cmp(
            str(extraction.path),
            str(Path('testing').joinpath('extractions')
                           .joinpath(extraction.path.relative_to(settings.EXTRACTIONS_PATH))),
            shallow=False
        )
