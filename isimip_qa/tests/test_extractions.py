import shutil
from pathlib import Path

import pandas as pd
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
    extractions_path = Path('testing') / ('extractions' if config.init_files else 'tmp')

    shutil.rmtree(extractions_path, ignore_errors=True)

    return init_settings(
        datasets_path=Path('testing') / 'datasets',
        extractions_path=extractions_path
    )

@pytest.mark.parametrize('dataset_path', datasets)
@pytest.mark.parametrize('extraction_class', extraction_classes)
def test_extraction(settings, dataset_path, extraction_class):
    dataset = Dataset(dataset_path)
    extraction = extraction_class(dataset)
    extraction.path.unlink(missing_ok=True)

    for file in dataset.files:
        file.open()
        extraction.extract(file)
        file.close()

    assert extraction.path.exists()
    assert extraction.path.suffix in ['.csv', '.json']

    template_path = Path('testing').joinpath('extractions') \
                                   .joinpath(extraction.path.relative_to(settings.EXTRACTIONS_PATH))

    if extraction.path.suffix == '.csv':
        pd.testing.assert_frame_equal(
            pd.read_csv(extraction.path),
            pd.read_csv(template_path)
        )
    else:
        assert extraction.path.read_text() == template_path.read_text()
