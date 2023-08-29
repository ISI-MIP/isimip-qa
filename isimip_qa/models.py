import logging
from pathlib import Path

import xarray as xr

from isimip_utils.patterns import match_dataset_path

from .config import settings

logger = logging.getLogger(__name__)


class Dataset:

    def __init__(self, dataset_path):
        self.path, self.specifiers = match_dataset_path(settings.PATTERN, Path(dataset_path))
        logger.info('match %s', self.path)

        # find files for dataset
        self.files = []
        abs_path = settings.DATASETS_PATH / dataset_path
        glob = sorted(abs_path.parent.glob(f'{abs_path.stem}*'))
        for index, file_path in enumerate(glob):
            first = (index == 0)
            last = (index == len(glob) - 1)
            self.files.append(File(file_path, index, first, last))

    def replace_name(self, **replacements):
        if self.path:
            name = self.path.name
            for identifier, specifiers in replacements.items():
                old = self.specifiers.get(identifier)
                new = '+'.join(specifiers) if isinstance(specifiers, list) else specifiers
                if old is not None:
                    name = name.replace(old.lower(), new.lower())
                else:
                    name = name + '_' + new
            return self.path.parent / name


class File:

    def __init__(self, file_path, index, first, last):
        self.path = file_path
        self.index = index
        self.first = first
        self.last = last

    def open(self):
        logger.info(f'load {self.path}')

        try:
            self.ds = xr.open_dataset(self.path, chunks={'time': 'auto'})
        except ValueError:
            # workaround for non standard times (e.g. growing seasons)
            self.ds = xr.open_dataset(self.path, chunks={'time': 'auto'}, decode_times=False)

        if settings.LOAD:
            self.ds.load()

    def close(self):
        self.ds.close()


class Region:

    def __init__(self, **kwargs):
        self.type = kwargs['type']
        self.specifier = kwargs['specifier']

        if self.type == 'point':
            self.lat = kwargs['lat']
            self.lon = kwargs['lon']

        elif self.type == 'mask':
            if kwargs['mask_path'] not in settings.MASKS:
                settings.MASKS[kwargs['mask_path']] = Mask(kwargs['mask_path'])
            self.mask = settings.MASKS[kwargs['mask_path']][kwargs['mask_variable']]


class Mask:

    def __init__(self, mask_path):
        self.ds = xr.load_dataset(settings.DATASETS_PATH / mask_path)

    def __getitem__(self, item):
        return self.ds[item]


class Extraction:

    region_types = None

    def extract(self, dataset, region, file):
        raise NotImplementedError

    def fetch(self, dataset, region):
        raise NotImplementedError

    def exists(self, dataset, region):
        raise NotImplementedError

    def write(self, ds, path, first):
        raise NotImplementedError

    def read(self, dataset, region):
        raise NotImplementedError

    def has_region(self, region):
        return self.region_types is None or region.type in self.region_types


class Assessment:

    extractions = None
    region_types = None

    def __init__(self, datasets, **kwargs):
        self.datasets = datasets

    def plot(self, extraction, region):
        raise NotImplementedError

    def has_extraction(self, extraction):
        return self.extractions is None or extraction.specifier in self.extractions

    def has_region(self, region):
        return self.region_types is None or region.type in self.region_types


class Subplot:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
