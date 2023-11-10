import shutil
from pathlib import Path

import numpy as np
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

    # compare to the template extraction
    template_path = Path('testing') / 'extractions' / extraction.path.relative_to(settings.EXTRACTIONS_PATH)

    if extraction.path.suffix == '.csv':
        df = pd.read_csv(extraction.path)
        template_df = pd.read_csv(template_path)
        pd.testing.assert_frame_equal(df, template_df)
    else:
        assert extraction.path.read_text() == template_path.read_text()

    # compare to the cdo extraction
    if extraction.specifier == 'mean':
        df = pd.read_csv(extraction.path)
        cdo_path = Path('testing') / 'cdo' / f'{dataset_path}_fldmean.csv'
        cdo_df = pd.read_csv(cdo_path, delim_whitespace=True, names=['time', 'var'])
        cdo_df['var'] = cdo_df['var'].astype(np.float64)
        pd.testing.assert_frame_equal(df, cdo_df)
