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

        if ds.time.size > 0:

            if self.region.type == 'mask':
                ds = ds.where(self.region.mask == 1)
            elif self.region.type == 'point':
                ds = ds.sel(lat=self.region.lat, lon=self.region.lon, method='nearest')

            var = next(iter(file.ds.data_vars.values()))
            array = ds[var.name].as_numpy()
            array_min = array.min().values
            array_max = array.max().values

            try:
                # if the range of the file extends the range of the stored histogram,
                # the range needs to be extended using the same step size
                step = self.bins[1] - self.bins[0]
                if array_min < self.bins[0]:
                    extension = np.arange(self.bins[0] - step, array_min, step, dtype=np.float64)
                    self.bins = np.concatenate((extension, self.bins))
                if array_max > self.bins[-1]:
                    extension = np.arange(self.bins[-1] + step, array_max, step, dtype=np.float64)
                    self.bins = np.concatenate((self.bins, extension))
            except AttributeError:
                self.bins = np.linspace(array_min, array_max, num=101, endpoint=True, dtype=np.float64)

            histogram = np.histogram(array, bins=self.bins)

            df = pd.DataFrame(data={
                'count': histogram[0]
            }, index=pd.Index(histogram[1][:-1], name='bin'), dtype=np.int64)

            try:
                self.df = self.df.reindex(df.index, fill_value=0) + df
            except AttributeError:
                self.df = df

        if file.last:
            logger.info(f'write {self.path}')
            self.write(self.df)
