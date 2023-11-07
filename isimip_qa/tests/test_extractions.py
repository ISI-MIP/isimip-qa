from pathlib import Path

import pytest

from isimip_qa.extractions import extraction_classes
from isimip_qa.models import Dataset

datasets = [
    'linear',
    'mask',
    'point',
    'sine'
]

@pytest.mark.parametrize('dataset_path', datasets)
@pytest.mark.parametrize('extraction_class', extraction_classes)
def test_extraction(config, settings, checksum, dataset_path, extraction_class):
    dataset = Dataset(dataset_path)
    extraction = extraction_class(dataset)
    extraction.path.unlink(missing_ok=True)

    for file in dataset.files:
        file.open()
        extraction.extract(file)
        file.close()

    assert extraction.path.exists()

    if not config.init_files:
        assert checksum(extraction.path) == checksum(
            Path('testing').joinpath('extractions')
                           .joinpath(extraction.path.relative_to(settings.EXTRACTIONS_PATH))
        )
