import logging

from ..mixins import CSVExtractionMixin, RemoteExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class CountExtraction(CSVExtractionMixin, RemoteExtractionMixin, Extraction):

    specifier = 'count'
    region_types = ['global', 'mask']

    def extract(self, file):
        logger.info(f'extract {self.region.specifier} {self.specifier} from {file.path}')

        ds = file.ds

        if self.period.type == 'slice':
            ds = ds.sel(time=slice(self.period.start_date, self.period.end_date))

        if self.region.type == 'mask':
            ds = ds.where(self.region.mask == 1)

        ds = ds.count(dim=('lat', 'lon'))

        logger.info(f'write {self.path}')
        self.write(ds, append=not file.first)
