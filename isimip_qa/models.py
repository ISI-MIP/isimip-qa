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
        return [File(file_path, index) for index, file_path in enumerate(sorted(glob))]

    def replace_name(self, **specifiers):
        name = self.path.name
        for identifier, specifiers in specifiers.items():
            old = self.specifiers[identifier]
            new = '+'.join(specifiers) if isinstance(specifiers, list) else specifiers
            name = name.replace(old.lower(), new.lower())
        return self.path.parent / name


class File(object):

    def __init__(self, file_path, index):
        self.path = file_path
        self.index = index

    def load(self):
        logger.info(f'load {self.path}')
        self.ds = xr.load_dataset(self.path)


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

    def extract(self, dataset, region, file):
        raise NotImplementedError

    def read(self, dataset, region):
        raise NotImplementedError

    def exists(self, dataset, region):
        raise NotImplementedError


class Assessment(object):

    extraction_classes = []

    def get_extraction(self, region):
        for extraction_class in self.extraction_classes:
            if region.type in extraction_class.region_types:
                return extraction_class()

    def plot(self, region):
        raise NotImplementedError
