import logging

from ..mixins import CSVExtractionMixin, RemoteExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class MeanExtraction(CSVExtractionMixin, RemoteExtractionMixin, Extraction):

    specifier = 'mean'
    region_types = ['global', 'mask', 'point']

    def extract(self, file):
        logger.info(f'extract {self.region.specifier} {self.specifier} from {file.path}')

        if self.region.type == 'mask':
            ds = file.ds.where(self.region.mask == 1).mean(dim=('lat', 'lon'), skipna=True)

        elif self.region.type == 'point':
            ds = file.ds.sel(lat=self.region.lat, lon=self.region.lon, method='nearest')

        else:
            ds = file.ds.mean(dim=('lat', 'lon'), skipna=True)

        logger.info(f'write {self.path}')
        self.write(ds, append=not file.first)
