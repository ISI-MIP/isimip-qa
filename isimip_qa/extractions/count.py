import logging

from ..mixins import CSVExtractionMixin, RemoteExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class CountExtraction(CSVExtractionMixin, RemoteExtractionMixin, Extraction):

    specifier = 'count'
    region_types = ['global', 'mask']

    def extract(self, file):
        logger.info(f'extract {self.region.specifier} {self.specifier} from {file.path}')

        if self.region.type == 'mask':
            ds = file.ds.where(self.region.mask == 1).count(dim=('lat', 'lon'))

        else:
            ds = file.ds.count(dim=('lat', 'lon'))

        logger.info(f'write {self.path}')
        self.write(ds, append=not file.first)
