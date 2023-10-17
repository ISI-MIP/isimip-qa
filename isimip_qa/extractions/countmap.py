import logging

from ..mixins import CSVExtractionMixin, RemoteExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class CountMapExtraction(CSVExtractionMixin, RemoteExtractionMixin, Extraction):

    specifier = 'countmap'
    region_types = ['global', 'mask']

    def extract(self, file):
        logger.info(f'extract {self.region.specifier} {self.specifier} from {file.path}')

        if self.region.type == 'mask':
            ds = file.ds.where(self.region.mask == 1).count(dim=('time',))
        else:
            ds = file.ds.count(dim=('time',))

        if file.first:
            self.ds = ds
        else:
            self.ds += ds

        if file.last:
            # only consider values > 0
            self.ds = self.ds.where(self.ds > 0)

            logger.info(f'write {self.path}')
            self.write(self.ds)
