import logging

from ..mixins import CSVExtractionMixin, RemoteExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class CountMapExtraction(CSVExtractionMixin, RemoteExtractionMixin, Extraction):

    specifier = 'countmap'
    region_types = ['global', 'mask']

    def extract(self, file):
        logger.info(f'extract {self.region.specifier} {self.specifier} from {file.path}')

        ds = file.ds

        if self.period.type == 'slice':
            ds = ds.sel(time=slice(self.period.start_date, self.period.end_date))

        if ds.time.size > 0:

            if self.region.type == 'mask':
                ds = ds.where(self.region.mask == 1)

            ds = ds.count(dim=('time',))

            try:
                self.ds += ds
            except AttributeError:
                self.ds = ds

        if file.last:
            # only consider values > 0
            self.ds = self.ds.where(self.ds > 0)

            logger.info(f'write {self.path}')
            self.write(self.ds)
