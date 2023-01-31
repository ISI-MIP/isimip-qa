import logging

import xarray as xr

from isimip_utils.decorators import cached_property
from isimip_utils.patterns import match_dataset_path

from .config import settings


logger = logging.getLogger(__name__)


class Dataset(object):

    def __init__(self, dataset_path):
        self.path, self.specifiers = match_dataset_path(settings.PATTERN, dataset_path)

    @cached_property
    def files(self):
        path = settings.DATASETS_PATH / self.path
        glob = path.parent.glob(f'{path.stem}*')
        return sorted(glob)

    def replace_name(self, **specifiers):
        name = self.path.name
        for identifier, specifiers in specifiers.items():
            old = self.specifiers[identifier]
            new = '+'.join(specifiers) if isinstance(specifiers, list) else specifiers
            name = name.replace(old.lower(), new.lower())
        return self.path.parent / name


class Region(object):

    def __init__(self, region):
        self.type = region['type']
        self.specifier = region['specifier']

        if self.type == 'point':
            self.lat = region['lat']
            self.lon = region['lon']

        elif self.type == 'mask':
            if region['mask_path'] not in settings.MASKS:
                settings.MASKS[region['mask_path']] = Mask(region['mask_path'])
            self.mask = settings.MASKS[region['mask_path']][region['mask_variable']]


class Mask(object):

    def __init__(self, mask_path):
        self.ds = xr.load_dataset(settings.DATASETS_PATH / mask_path)

    def __getitem__(self, item):
        return self.ds[item]


class Extraction(object):

    def get_path(self, dataset, region):
        raise NotImplementedError

    def extract(self, dataset, region):
        raise NotImplementedError

    @property
    def is_complete(self):
        complete = True
        for dataset in settings.DATASETS:
            for region in settings.REGIONS:
                complete &= self.get_path(dataset, region).exists()
        return complete

    @staticmethod
    def run():
        is_complete = all([extraction.is_complete for extraction in settings.EXTRACTIONS])
        if is_complete:
            return

        for dataset in settings.DATASETS:
            for file_path in dataset.files:
                logger.info(f'load {file_path}')
                ds = xr.load_dataset(file_path)

                for extraction in settings.EXTRACTIONS:
                    for region in settings.REGIONS:
                        if region.type in extraction.region_types:
                            extraction.extract(dataset, region, ds)


class Assessment(object):

    extraction_classes = []

    def get_path(self, dataset, region):
        raise NotImplementedError

    def plot(self):
        raise NotImplementedError

    @staticmethod
    def run():
        for assessment in settings.ASSESSMENTS:
            assessment.plot()
