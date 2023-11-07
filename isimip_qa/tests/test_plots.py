import filecmp
from pathlib import Path

import pytest

from isimip_qa.extractions import extraction_classes
from isimip_qa.models import Dataset
from isimip_qa.plots import plot_classes

datasets = [
    'linear',
    'mask',
    'point',
    'sine'
]

@pytest.mark.parametrize('dataset_path', datasets)
@pytest.mark.parametrize('extraction_class', extraction_classes)
@pytest.mark.parametrize('plot_class', plot_classes)
def test_mean_extraction(config, settings, dataset_path, extraction_class, plot_class):
    dataset = Dataset(dataset_path)
    if plot_class.has_extraction(extraction_class):
        plot = plot_class(extraction_class, [dataset], path=dataset.path.stem)
        plot.create()
        print(plot.get_subplots())
        for sp in plot.get_subplots():
            assert sp.path.exists()

            if not config.init_files:
                assert filecmp.cmp(
                    sp.path,
                    Path('testing').joinpath('plots')
                                   .joinpath(sp.path.relative_to(settings.PLOTS_PATH)),
                    shallow=False
                )
