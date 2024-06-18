import logging
from pathlib import Path

import cftime
import xarray as xr

from .config import settings

logger = logging.getLogger(__name__)


class Dataset:

    def __init__(self, dataset_path):
        self.path = Path(dataset_path).with_suffix('')

        # find files for dataset
        self.files = []
        abs_path = settings.DATASETS_PATH / dataset_path
        glob = sorted(abs_path.parent.glob(f'{abs_path.stem}*'))
        for index, file_path in enumerate(glob):
            first = (index == 0)
            last = (index == len(glob) - 1)
            self.files.append(File(file_path, index, first, last))

    def  __repr__(self):
        return str(self.path)

    def replace_name(self, **replacements):
        if self.path:
            name = self.path.name
            for key, value in replacements.items():
                if key == 'region' and '_global_' in name:
                    name = name.replace('_global_', f'_{value}_')
                else:
                    name = name + '_' + value
            return self.path.parent / name


class File:

    def __init__(self, file_path, index, first, last):
        self.path = file_path
        self.index = index
        self.first = first
        self.last = last

    def open(self):
        logger.info(f'open {self.path}')

        try:
            self.ds = xr.open_dataset(self.path)
        except ValueError:
            # workaround for non standard times (e.g. growing seasons)
            self.ds = xr.open_dataset(self.path, decode_times=False)

            if self.ds['time'].units.startswith('growing seasons'):
                units = self.ds['time'].units.replace('growing seasons', 'common_years')
                times = cftime.num2date(self.ds['time'], units, calendar='365_day')

                self.ds['time'] = times

        if settings.LOAD:
            logger.info(f'load {self.path}')
            self.ds.load()

    def close(self):
        logger.info(f'close {self.path}')
        self.ds.close()
        del self.ds


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

    def __init__(self, path):
        path = Path(path).expanduser()
        if not path.is_absolute():
            path = settings.DATASETS_PATH / path

        self.ds = xr.load_dataset(path)

    def __getitem__(self, item):
        return self.ds[item]


class Period:

    def __init__(self, **kwargs):
        self.type = kwargs['type']

        if self.type == 'slice':
            self.start_date = str(kwargs['start_date'])
            self.end_date = str(kwargs['end_date'])


class Extraction:

    region_types = None
    period_types = None

    def __init__(self, dataset, region=None, period=None, gridarea=None):
        self.dataset = dataset
        self.region = region or Region(type='global', specifier='global')
        self.period = period or Period(type='auto')
        self.gridarea = gridarea

    @property
    def path(self):
        raise NotImplementedError

    def exists(self):
        return self.path.exists()

    def fetch(self):
        raise NotImplementedError

    def extract(self, file):
        raise NotImplementedError

    def read(self):
        raise NotImplementedError

    @classmethod
    def has_region(cls, region):
        return cls.region_types is None or region.type in cls.region_types

    @classmethod
    def has_period(cls, period):
        return cls.period_types is None or period.type in cls.period_types


class Plot:

    extraction_classes = None
    region_types = None
    period_types = None

    def __init__(self, extraction_class, datasets, region=None, period=None, **kwargs):
        self.extraction_class = extraction_class
        self.datasets = datasets
        self.region = region or Region(type='global', specifier='global')
        self.period = period or Period(type='auto')

    def create(self):
        raise NotImplementedError

    @classmethod
    def has_extraction(cls, extraction):
        return cls.extractions is None or extraction.specifier in cls.extractions

    @classmethod
    def has_region(cls, region):
        return cls.region_types is None or region.type in cls.region_types

    @classmethod
    def has_period(cls, period):
        return cls.period_types is None or period.type in cls.period_types


class Subplot:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
