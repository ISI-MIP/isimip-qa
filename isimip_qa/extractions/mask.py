import logging

from ..mixins import CSVExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class MaskExtraction(CSVExtractionMixin, Extraction):

    region_types = ['mask']

    def extract(self, dataset, region, file):
        csv_path = self.get_csv_path(dataset, region)
        logger.info(f'extract to {csv_path}')

        ds = file.ds.where(region.mask == 1).mean(dim=('lat', 'lon'))
        var = next(iter(file.ds.data_vars.values()))

        self.write_csv(ds, var.attrs, csv_path, first_file=(file.index == 0))
