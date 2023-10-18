import logging

import numpy as np
import pandas as pd

from ..mixins import CSVExtractionMixin, RemoteExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class HistogramExtraction(CSVExtractionMixin, RemoteExtractionMixin, Extraction):

    specifier = 'histogram'
    region_types = ['global', 'mask', 'point']

    def extract(self, file):
        logger.info(f'extract {self.region.specifier} {self.specifier} from {file.path}')

        ds = file.ds

        if self.period.type == 'slice':
            ds = ds.sel(time=slice(self.period.start_date, self.period.end_date))

        if self.region.type == 'mask':
            ds = ds.where(self.region.mask == 1)
        elif self.region.type == 'point':
            ds = ds.sel(lat=self.region.lat, lon=self.region.lon, method='nearest')

        var = next(iter(file.ds.data_vars.values()))
        array = ds[var.name].as_numpy()
        array_range = (array.min().values, array.max().values)

        histogram = np.histogram(array, bins=100, range=array_range)

        df = pd.DataFrame(data={
            'count': histogram[0]
        }, dtype=np.float64, index=pd.Index(histogram[1][1:], name='bin'))

        if file.first:
            self.df = df
        else:
            self.df += df

        if file.last:
            logger.info(f'write {self.path}')
            self.write(self.df)
