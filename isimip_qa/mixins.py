import itertools
import json
import logging
from collections import defaultdict
from itertools import product

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from .config import settings
from .models import Subplot

from .exceptions import ExtractionNotFound

logger = logging.getLogger(__name__)


class CSVExtractionMixin:

    def get_path(self, dataset, region):
        path = dataset.replace_name(region=region.specifier, extraction=self.specifier)
        return settings.EXTRACTIONS_PATH.joinpath(path).with_suffix('.csv')

    def exists(self, dataset, region):
        return self.get_path(dataset, region).exists()

    def write(self, ds, path, first):
        if len(ds.dims) == 3:
            dim_order = ('lon', 'lat', 'time')
        elif len(ds.dims) == 2:
            dim_order = ('lon', 'lat')
        else:
            dim_order = ('time', )

        if first:
            path.parent.mkdir(exist_ok=True, parents=True)
            ds.to_dataframe(dim_order=dim_order).to_csv(path)
        else:
            ds.to_dataframe(dim_order=dim_order).to_csv(path, mode='a', header=False)

    def read(self, dataset, region):
        # pandas cannot handle datetimes before 1677-09-22 so we need to
        # manually set every timestamp before to None using a custom date_parser
        def parse_time(time):
            try:
                try:
                    return pd.Timestamp(np.datetime64(time))
                except ValueError:
                    # workaround for non standard times (e.g. growing seasons)
                    return pd.Timestamp(year=int(time), month=1, day=1)
            except pd.errors.OutOfBoundsDatetime:
                return pd.NaT

        # get the csv_path
        path = self.get_path(dataset, region)

        # read the dataframe from the csv
        try:
            df = pd.read_csv(path)
        except FileNotFoundError:
            raise ExtractionNotFound

        if 'time' in df:
            # parse the time axis of the dataframe
            df['time'] = df['time'].apply(parse_time)

            # remove all values without time
            df = df[df.time.notnull()]
            df.set_index('time', inplace=True)

        return df


class JSONExtractionMixin:

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


class NetCdfExtractionMixin:

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


class ConcatExtractionMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ds = defaultdict(dict)
        self.n = defaultdict(dict)

    def concat(self, dataset, region, ds, n):
        if dataset not in self.ds:
            self.ds[dataset] = {}
            self.n[dataset] = {}

        if region not in self.ds[dataset]:
            self.ds[dataset][region] = ds
            self.n[dataset][region] = n
        else:
            self.ds[dataset][region] += ds
            self.n[dataset][region] += n


class PlotMixin:

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name', None)
        self.ymin = self.ymax = self.vmin = self.vmax = {}
        super().__init__(*args, **kwargs)

    def get_path(self, extraction, region):
        if self.name:
            name = self.name

            # overwrite _global_ with the region, this is not very elegant,
            # but after a lot (!) of experiments, this is the best solution ...
            name = name.replace('_global_', '_' + region.specifier + '_')

            # add the extration and the assessment specifiers
            name = name + '_' + extraction.specifier + '_' + self.specifier

            return settings.ASSESSMENTS_PATH / name


class SVGPlotMixin(PlotMixin):

    def get_path(self, extraction, region):
        path = super().get_path(extraction, region)
        if path:
            return path.with_suffix('.svg')


class PNGPlotMixin(PlotMixin):

    def get_path(self, extraction, region):
        path = super().get_path(extraction, region)
        if path:
            return path.with_suffix('.png')


class GridPlotMixin:

    def __init__(self, *args, **kwargs):
        self.dimensions = kwargs.pop('dimensions', None)
        self.grid = kwargs.pop('grid', 2)
        if self.dimensions:
            self.keys = list(self.dimensions.keys())
            self.permutations = list(product(*self.dimensions.values()))
        super().__init__(*args, **kwargs)

    def get_figure(self, nrows, ncols, ratio=1):
        fig, axs = plt.subplots(nrows, ncols, squeeze=False, figsize=(6 * ratio * ncols, 6 * nrows))
        for ax in itertools.chain.from_iterable(axs):
            ax.tick_params(bottom=False, labelbottom=False, left=False, labelleft=False)
        return fig, axs

    def get_grid(self):
        grid = [1, 1]
        if self.dimensions:
            for d, j in enumerate([1, 0]):
                if self.grid > j:
                    try:
                        key = self.keys[j]
                        grid[d] = len(self.dimensions[key])
                    except IndexError:
                        pass
        return grid

    def get_grid_indexes(self, i):
        grid_indexes = [0, 0]
        if self.dimensions:
            for d, j in enumerate([1, 0]):
                if self.grid > j:
                    try:
                        key = self.keys[j]
                        value = self.permutations[i][j]
                        grid_indexes[d] = self.dimensions[key].index(value)
                    except IndexError:
                        pass
        return grid_indexes

    def get_subplots(self, extraction, region):
        subplots = []
        for index, dataset in enumerate(self.datasets):
            try:
                df = self.get_df(extraction, dataset, region)
            except ExtractionNotFound:
                continue

            try:
                attrs = self.get_attrs(extraction, dataset, region)
            except ExtractionNotFound:
                attrs = {}

            var = df.columns[-1]
            irow, icol = self.get_grid_indexes(index)

            subplot = Subplot(
                df=df,
                attrs=attrs,
                var=var,
                label=self.get_label(index),
                title=self.get_title(index),
                irow=irow,
                icol=icol,
                primary=dataset.primary
            )

            subplots.append(subplot)

        return subplots

    def get_title(self, i):
        if self.dimensions:
            t = []
            for j in [1, 0]:
                if self.grid > j:
                    try:
                        t.append(self.permutations[i][j])
                    except IndexError:
                        pass
            return ' '.join(t)

    def get_label(self, i):
        if self.dimensions:
            return ' '.join(self.permutations[i][self.grid:])

    def get_ymin(self, irow, icol, subplots):
        if settings.YMIN is None:
            return min([sp.df[sp.var].min() for sp in subplots if sp.irow == irow and sp.icol == icol]) * 0.99
        else:
            return settings.YMIN

    def get_ymax(self, irow, icol, subplots):
        if settings.YMAX is None:
            return max([sp.df[sp.var].max() for sp in subplots if sp.irow == irow and sp.icol == icol]) * 1.01
        else:
            return settings.YMAX

    def get_vmin(self, irow, icol, subplots):
        if settings.VMIN is None:
            return min([sp.df[sp.var].min() for sp in subplots if sp.irow == irow and sp.icol == icol])
        else:
            return settings.VMIN

    def get_vmax(self, irow, icol, subplots):
        if settings.VMAX is None:
            return max([sp.df[sp.var].max() for sp in subplots if sp.irow == irow and sp.icol == icol])
        else:
            return settings.VMAX
