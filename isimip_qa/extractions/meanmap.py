import logging

from ..mixins import CSVExtractionMixin, RemoteExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class MeanMapExtraction(CSVExtractionMixin, RemoteExtractionMixin, Extraction):

    specifier = 'meanmap'
    region_types = ['global', 'mask']

    def extract(self, file):
        logger.info(f'extract {self.region.specifier} {self.specifier} from {file.path}')

        if self.region.type == 'mask':
            ds = file.ds.where(self.region.mask == 1).sum(dim=('time',), skipna=True, min_count=1)
        else:
            ds = file.ds.sum(dim=('time',), skipna=True, min_count=1)

        if file.first:
            self.ds = ds
            self.count = len(file.ds.time)
        else:
            self.ds += ds
            self.count += len(file.ds.time)

        if file.last:
            # devide sum by count to get mean
            self.ds /= self.count

            logger.info(f'write {self.path}')
            self.write(self.ds)
