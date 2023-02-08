import json
import logging

import pandas as pd

from .config import settings

logger = logging.getLogger(__name__)


class CSVExtractionMixin(object):

    def get_csv_path(self, dataset, region):
        path = dataset.replace_name(region=region.specifier)
        path = path.with_name(path.name + '_' + self.specifier)
        return settings.EXTRACTIONS_PATH.joinpath(path).with_suffix('.csv')

    def write_csv(self, ds, attrs, csv_path, first_file):
        if first_file:
            csv_path.parent.mkdir(exist_ok=True, parents=True)
            ds.to_dataframe().to_csv(csv_path)
            json.dump(attrs, csv_path.with_suffix('.json').open('w'))
        else:
            ds.to_dataframe().to_csv(csv_path, mode='a', header=False)

    def exists(self, dataset, region):
        csv_path = self.get_csv_path(dataset, region)
        return csv_path.exists() and csv_path.with_suffix('.json').exists()

    def read(self, dataset, region):
        csv_path = self.get_csv_path(dataset, region)
        return (
            pd.read_csv(csv_path, index_col='time', parse_dates=['time'], infer_datetime_format=True),
            json.load(csv_path.with_suffix('.json').open())
        )


class SVGPlotMixin(object):

    def get_svg_path(self, dataset, region, extraction):
        path = dataset.replace_name(region=region.specifier, time_step=self.specifier, **settings.SPECIFIERS)
        path = path.with_name(path.name + '_' + extraction.specifier)
        return settings.ASSESSMENTS_PATH.joinpath(path.name).with_suffix('.svg')


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
