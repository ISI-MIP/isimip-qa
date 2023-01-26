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
            mask_ds = xr.load_dataset(settings.DATASETS_PATH / region['mask_path'])
            self.mask = mask_ds[region['mask_variable']]


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


class Assessment(object):

    extraction_classes = []

    def get_path(self, dataset, region):
        raise NotImplementedError

    def plot(self):
        raise NotImplementedError
