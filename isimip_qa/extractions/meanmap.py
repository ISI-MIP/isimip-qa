import logging

from ..mixins import CSVExtractionMixin, RemoteExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class MeanMapExtraction(CSVExtractionMixin, RemoteExtractionMixin, Extraction):

    specifier = 'meanmap'
    region_types = ['global', 'mask']

    def extract(self, file):
        logger.info(f'extract {self.region.specifier} {self.specifier} from {file.path}')

        ds = file.ds

        if self.period.type == 'slice':
            ds = ds.sel(time=slice(self.period.start_date, self.period.end_date))

        if ds.time.size > 0:

            if self.region.type == 'mask':
                ds = ds.where(self.region.mask == 1)

            ds = ds.sum(dim=('time',), skipna=True, min_count=1)

            try:
                self.ds += ds
                self.count += len(file.ds.time)
            except AttributeError:
                self.ds = ds
                self.count = len(file.ds.time)

        if file.last:
            # devide sum by count to get mean
            self.ds /= self.count

            logger.info(f'write {self.path}')
            self.write(self.ds)
