import logging

from ..mixins import CSVExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class CountExtraction(CSVExtractionMixin, Extraction):

    specifier = 'count'
    region_types = ['global', 'mask']

    def extract(self, dataset, region, file):
        logger.info(f'extract {region.specifier} {self.specifier} from {file.path}')

        if region.type == 'mask':
            ds = file.ds.where(region.mask == 1).count(dim=('lat', 'lon'))

        else:
            ds = file.ds.count(dim=('lat', 'lon'))

        path = self.get_path(dataset, region)
        logger.info(f'write {path}')
        self.write(ds, path, first=file.first)
