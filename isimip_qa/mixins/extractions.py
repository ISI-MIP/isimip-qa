import json
import logging

import numpy as np
import pandas as pd
import xarray as xr

from isimip_utils.fetch import fetch_file

from ..config import settings
from ..exceptions import ExtractionNotFound

logger = logging.getLogger(__name__)


class RemoteExtractionMixin:

    def fetch(self):
        if settings.EXTRACTIONS_LOCATIONS:
            path = self.path.relative_to(settings.EXTRACTIONS_PATH)
            file_content = fetch_file(settings.EXTRACTIONS_LOCATIONS, path)
            if file_content is not None:
                logger.info('fetch %s', path)
                self.path.parent.mkdir(exist_ok=True, parents=True)
                self.path.open('wb').write(file_content)
                return self.path
            else:
                logger.info('could not fetch %s', path)


class NetCDFExtractionMixin:

    @property
    def path(self):
        replacements = {'region': self.region.specifier, 'extraction': self.specifier}
        if self.period.type == 'slice':
            replacements.update({'start_date': self.period.start_date, 'end_date': self.period.end_date})

        path = self.dataset.replace_name(**replacements)
        return settings.EXTRACTIONS_PATH.joinpath(path).with_suffix('.nc')

    def write(self):
        self.path.parent.mkdir(exist_ok=True, parents=True)

        for varname, attrs in self.attrs.items():
            self.ds[varname].attrs.update(attrs)

        encoding = {}
        for varname in self.ds.variables:
            encoding[varname] = {'dtype': np.dtype('float64'), '_FillValue': 1e+20}
            if varname in self.attrs.keys():
                encoding[varname]['zlib'] = True

        self.ds.to_netcdf(self.path, format='NETCDF4_CLASSIC', encoding=encoding)

    def read(self):
        return xr.open_dataset(self.path)

    def concat(self, ds, dim='time'):
        try:
            self.ds = xr.concat([self.ds, ds], dim)
        except AttributeError:
            self.ds = ds.copy()
        del ds


class CSVExtractionMixin:

    @property
    def path(self):
        replacements = {'region': self.region.specifier, 'extraction': self.specifier}
        if self.period.type == 'slice':
            replacements.update({'start_date': self.period.start_date, 'end_date': self.period.end_date})

        path = self.dataset.replace_name(**replacements)
        return settings.EXTRACTIONS_PATH.joinpath(path).with_suffix('.csv')

    def write(self, data, append=False):
        if isinstance(data, xr.core.dataset.Dataset):
            # this is a xarray dataset, so we convert it to a dataframe
            ds = data
            if set(ds.dims) == {'lon', 'lat', 'time'}:
                dim_order = ('lon', 'lat', 'time')
            elif set(ds.dims) == {'lon', 'lat'}:
                dim_order = ('lon', 'lat')
            else:
                dim_order = tuple(ds.dims)

            df = ds.to_dataframe(dim_order=dim_order)
        else:
            # this is a pandas dataframe
            df = data

        if append:
            df.to_csv(self.path, mode='a', header=False)
        else:
            self.path.parent.mkdir(exist_ok=True, parents=True)
            df.to_csv(self.path)

    def read(self):
        # pandas cannot handle datetimes before 1677-09-22 so we need to
        # manually set every timestamp before to None using a custom date_parser
        def parse_time(time):
            try:
                return pd.Timestamp(np.datetime64(time))
            except pd.errors.OutOfBoundsDatetime:
                return pd.NaT

        # read the dataframe from the csv
        try:
            df = pd.read_csv(self.path)
        except FileNotFoundError as e:
            raise ExtractionNotFound from e

        if 'time' in df:
            # parse the time axis of the dataframe
            df['time'] = df['time'].apply(parse_time)

            # remove all values without time
            df = df[df.time.notnull()]
            df.set_index('time', inplace=True)

        return df


class JSONExtractionMixin:

    @property
    def path(self):
        path = self.dataset.replace_name(region=self.region.specifier)
        path = path.with_name(path.name + '_' + self.specifier)
        return settings.EXTRACTIONS_PATH.joinpath(path).with_suffix('.json')

    def write(self, data):
        self.path.parent.mkdir(exist_ok=True, parents=True)
        json.dump(data, self.path.open('w'))

    def read(self):
        return json.load(self.path.open())
