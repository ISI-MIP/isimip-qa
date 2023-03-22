import json
import logging

import numpy as np
import pandas as pd
import xarray as xr

from .config import settings

logger = logging.getLogger(__name__)


class CSVExtractionMixin(object):

    def get_path(self, dataset, region):
        path = dataset.replace_name(region=region.specifier)
        path = path.with_name(path.name + '_' + self.specifier)
        return settings.EXTRACTIONS_PATH.joinpath(path).with_suffix('.csv')

    def exists(self, dataset, region):
        return self.get_path(dataset, region).exists()

    def write(self, ds, path, first):
        if first:
            path.parent.mkdir(exist_ok=True, parents=True)
            ds.to_dataframe().to_csv(path)
        else:
            ds.to_dataframe().to_csv(path, mode='a', header=False)

    def read(self, dataset, region):
        # pandas cannot handle datetimes before 1677-09-22 so we need to
        # manually set every timestamp before to None using a custom date_parser
        def parse_timestamps(timestamp):
            try:
                return pd.Timestamp(np.datetime64(timestamp))
            except pd.errors.OutOfBoundsDatetime:
                return pd.NaT

        # get the csv_path
        path = self.get_path(dataset, region)

        # read the dataframe from the csv
        df = pd.read_csv(path, parse_dates=['time'], date_parser=parse_timestamps)
        df = df[df.time.notnull()]
        df.set_index('time', inplace=True)

        return df


class JSONExtractionMixin(object):

    def get_path(self, dataset, region):
        path = dataset.replace_name(region=region.specifier)
        path = path.with_name(path.name + '_' + self.specifier)
        return settings.EXTRACTIONS_PATH.joinpath(path).with_suffix('.json')

    def exists(self, dataset, region):
        return self.get_path(dataset, region).exists()

    def write(self, data, path):
        path.parent.mkdir(exist_ok=True, parents=True)
        json.dump(data, path.open('w'))

    def read(self, dataset, region):
        path = self.get_path(dataset, region)
        return json.load(path.open())


class NetCdfExtractionMixin(object):

    def get_path(self, dataset, region):
        path = dataset.replace_name(region=region.specifier)
        path = path.with_name(path.name + '_' + self.specifier)
        return settings.EXTRACTIONS_PATH.joinpath(path).with_suffix('.nc')

    def exists(self, dataset, region):
        return self.get_path(dataset, region).exists()

    def write(self, ds, path):
        path.parent.mkdir(exist_ok=True, parents=True)

        # remove globa attributes
        ds.attrs = {}

        ds.lat.attrs['_FillValue'] = 1.e+20
        ds.lon.attrs['_FillValue'] = 1.e+20
        ds.time.attrs['_FillValue'] = 1.e+20

        ds.to_netcdf(path, unlimited_dims=['time'], format='NETCDF4_CLASSIC')

    def read(self, dataset, region):
        path = self.get_path(dataset, region)
        return xr.load_dataset(settings.DATASETS_PATH / path)


class PlotMixin(object):

    def get_path(self, dataset, region, extraction):
        settings_specifiers = {}
        for identifier, specifiers in settings.SPECIFIERS.items():
            settings_specifiers[identifier] = ['various'] if len(specifiers) > 5 else specifiers

        path = dataset.replace_name(region=region.specifier, time_step=self.specifier, **settings_specifiers)
        path = path.with_name(path.name + '_' + extraction.specifier)
        return settings.ASSESSMENTS_PATH.joinpath(path.name)


class SVGPlotMixin(PlotMixin):

    def get_path(self, dataset, region, extraction):
        return super().get_path(dataset, region, extraction).with_suffix('.svg')


class PNGPlotMixin(PlotMixin):

    def get_path(self, dataset, region, extraction):
        return super().get_path(dataset, region, extraction).with_suffix('.png')


class GridPlotMixin(object):

    def get_grid(self):
        g = [1, 1]
        for d, j in enumerate([1, 0]):
            if settings.GRID > j:
                try:
                    identifier = settings.IDENTIFIERS[j]
                    g[d] = len(settings.SPECIFIERS[identifier])
                except IndexError:
                    pass
        return g

    def get_grid_indexes(self, i):
        gi = [0, 0]
        for d, j in enumerate([1, 0]):
            if settings.GRID > j:
                try:
                    identifier = settings.IDENTIFIERS[j]
                    specifier = settings.PERMUTATIONS[i][j]
                    gi[d] = settings.SPECIFIERS[identifier].index(specifier)
                except IndexError:
                    pass
        return gi

    def get_title(self, i):
        t = []
        for j in [1, 0]:
            if settings.GRID > j:
                try:
                    t.append(settings.PERMUTATIONS[i][j])
                except IndexError:
                    pass
        return ' '.join(t)

    def get_label(self, i):
        return ' '.join(settings.PERMUTATIONS[i][settings.GRID:])
