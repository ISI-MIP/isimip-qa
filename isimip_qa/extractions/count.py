import logging

from ..mixins import CSVExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class CountExtraction(CSVExtractionMixin, Extraction):

    specifier = 'count'
    region_types = ['global', 'mask']

    def extract(self, dataset, region, file):
        csv_path = self.get_csv_path(dataset, region)
        logger.info(f'extract to {csv_path}')

        var = next(iter(file.ds.data_vars.values()))
        attrs = var.attrs

        if region.type == 'mask':
            ds = file.ds.where(region.mask == 1).count(dim=('lat', 'lon'))

        else:
            ds = file.ds.count(dim=('lat', 'lon'))

        self.write_csv(ds, attrs, csv_path, first_file=(file.index == 0))
