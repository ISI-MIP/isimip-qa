import logging

import numpy as np

from ..mixins import NetCDFExtractionMixin, RemoteExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class MeanExtraction(NetCDFExtractionMixin, RemoteExtractionMixin, Extraction):

    specifier = 'mean'
    region_types = ['global', 'mask', 'point']

    def extract(self, file):
        logger.info(f'extract {self.region.specifier} {self.specifier} from {file.path}')

        ds = file.ds

        if self.period.type == 'slice':
            ds = ds.sel(time=slice(self.period.start_date, self.period.end_date))

        if self.region.type == 'point':
            ds = ds.sel(lat=self.region.lat, lon=self.region.lon, method='nearest')
        else:
            if self.region.type == 'mask':
                ds = ds.where(self.region.mask == 1)

            if self.gridarea is None:
                weights = np.sin(np.deg2rad(ds.lat + 0.25)) - np.sin(np.deg2rad(ds.lat - 0.25))
            else:
                weights = self.gridarea

            ds = ds.weighted(weights).mean(dim=('lat', 'lon'), skipna=True)

        self.concat(ds)

        if file.first:
            self.attrs = {varname: var.attrs for varname, var in file.ds.data_vars.items()}

        if file.last:
            logger.info(f'write {self.path}')
            self.write()
