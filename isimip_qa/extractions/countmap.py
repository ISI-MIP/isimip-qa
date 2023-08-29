import logging

from ..mixins import ConcatExtractionMixin, CSVExtractionMixin, RemoteExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class MeanMapExtraction(ConcatExtractionMixin, CSVExtractionMixin, RemoteExtractionMixin, Extraction):

    specifier = 'countmap'
    region_types = ['global', 'mask']

    def extract(self, dataset, region, file):
        logger.info(f'extract {region.specifier} {self.specifier} from {file.path}')

        if region.type == 'mask':
            ds = file.ds.where(region.mask == 1).count(dim=('time',))
        else:
            ds = file.ds.count(dim=('time',))

        n = len(file.ds.time)

        self.concat(dataset, region, ds, n)

        if file.last:
            self.ds[dataset][region] = self.ds[dataset][region].where(self.ds[dataset][region] > 0)

            path = self.get_path(dataset, region)
            logger.info(f'write {path}')
            self.write(self.ds[dataset][region], path, first=True)
