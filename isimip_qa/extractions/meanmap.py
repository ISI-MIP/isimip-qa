import logging
from collections import defaultdict

from ..mixins import ConcatExtractionMixin, CSVExtractionMixin, RemoteExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class MeanMapExtraction(ConcatExtractionMixin, CSVExtractionMixin, RemoteExtractionMixin, Extraction):

    specifier = 'meanmap'
    region_types = ['global', 'mask']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ds = defaultdict(dict)
        self.n = defaultdict(dict)

    def extract(self, dataset, region, file):
        logger.info(f'extract {region.specifier} {self.specifier} from {file.path}')

        if region.type == 'mask':
            ds = file.ds.where(region.mask == 1).sum(dim=('time',), min_count=1)
        else:
            ds = file.ds.sum(dim=('time',), min_count=1)

        n = len(file.ds.time)

        self.concat(dataset, region, ds, n)

        if file.last:
            self.ds[dataset][region] /= self.n[dataset][region]

            path = self.get_path(dataset, region)
            logger.info(f'write {path}')
            self.write(self.ds[dataset][region], path, first=True)
