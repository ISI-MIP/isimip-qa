import logging

from ..mixins import CSVExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class PointExtraction(CSVExtractionMixin, Extraction):

    region_types = ['point']

    def extract(self, dataset, region, file):
        csv_path = self.get_csv_path(dataset, region)
        logger.info(f'extract to {csv_path}')

        ds = file.ds.sel(lat=region.lat, lon=region.lon, method='nearest')
        var = next(iter(file.ds.data_vars.values()))

        self.write_csv(ds, var.attrs, csv_path, first_file=(file.index == 0))
