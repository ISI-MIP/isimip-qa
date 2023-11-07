import shutil
from pathlib import Path

import pytest
from skimage.io import imread
from skimage.metrics import structural_similarity as ssim

from isimip_qa.extractions import extraction_classes
from isimip_qa.main import init_settings
from isimip_qa.models import Dataset
from isimip_qa.plots import plot_classes

datasets = [
    'linear',
    'mask',
    'point',
    'sine'
]

@pytest.fixture(scope='module')
def settings(config):
    extractions_path = Path('testing') / 'extractions'
    plots_path = Path('testing') / ('plots' if config.init_files else 'tmp')

    shutil.rmtree(plots_path, ignore_errors=True)

    return init_settings(
        datasets_path=Path('testing') / 'datasets',
        extractions_path=extractions_path,
        plots_path=plots_path,
        plots_format='png'
    )

@pytest.mark.parametrize('dataset_path', datasets)
@pytest.mark.parametrize('extraction_class', extraction_classes)
@pytest.mark.parametrize('plot_class', plot_classes)
def test_plot(settings, dataset_path, extraction_class, plot_class):
    dataset = Dataset(dataset_path)
    if plot_class.has_extraction(extraction_class):
        plot = plot_class(extraction_class, [dataset], path=dataset.path.stem)
        plot.create()

        for sp in plot.get_subplots():
            assert sp.path.exists()

            img = imread(sp.path, as_gray=True)

            template_path = Path('testing').joinpath('plots') \
                                           .joinpath(sp.path.relative_to(settings.PLOTS_PATH))
            template_img = imread(template_path, as_gray=True)

            similarity = ssim(img, template_img, data_range=template_img.max() - template_img.min())

            assert similarity == 1.0
