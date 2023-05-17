import logging

import xarray as xr

from isimip_utils.patterns import match_dataset_path

from .config import settings


logger = logging.getLogger(__name__)


class Dataset(object):

    def __init__(self, dataset_path):
        path = settings.DATASETS_PATH / dataset_path
        glob = sorted(path.parent.glob(f'{path.stem}*'))

        # find files for dataset
        self.files = []
        for index, file_path in enumerate(glob):
            first = (index == 0)
            last = (index == len(glob) - 1)
            self.files.append(File(file_path, index, first, last))

        if self.files:
            first_file_path = self.files[0].path
            self.path, self.specifiers = match_dataset_path(settings.PATTERN, first_file_path)
        else:
            self.path, self.specifiers = None, {}

    def replace_name(self, **specifiers):
        if self.path:
            name = self.path.name
            for identifier, specifiers in specifiers.items():
                old = self.specifiers.get(identifier)
                new = '+'.join(specifiers) if isinstance(specifiers, list) else specifiers
                if old is not None:
                    name = name.replace(old.lower(), new.lower())
                else:
                    name = name + '_' + new
            return self.path.parent / name


class File(object):

    def __init__(self, file_path, index, first, last):
        self.path = file_path
        self.index = index
        self.first = first
        self.last = last

    def load(self):
        logger.info(f'load {self.path}')
        if settings.LOAD:
            self.ds = xr.load_dataset(self.path)
        else:
            self.ds = xr.open_dataset(self.path)

    def unload(self):
        self.ds.close()


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

    region_types = None

    def extract(self, dataset, region, file, ds):
        raise NotImplementedError

    def read(self, dataset, region):
        raise NotImplementedError

    def exists(self, dataset, region):
        raise NotImplementedError


class Assessment(object):

    extractions = None
    region_types = None

    def get_extraction(self, extraction, region):
        for extraction_class in self.extraction_classes:
            if region.type in extraction_class.region_types:
                return extraction_class()

    def plot(self, region):
        raise NotImplementedError
