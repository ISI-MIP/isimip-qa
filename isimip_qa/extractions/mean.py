import logging

from ..mixins import CSVExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class MeanExtraction(CSVExtractionMixin, Extraction):

    specifier = 'mean'
    region_types = ['global', 'mask', 'point']

    def extract(self, dataset, region, file):
        csv_path = self.get_csv_path(dataset, region)
        logger.info(f'extract to {csv_path}')

        var = next(iter(file.ds.data_vars.values()))
        attrs = var.attrs

        if region.type == 'mask':
            ds = file.ds.where(region.mask == 1).mean(dim=('lat', 'lon'))

        elif region.type == 'point':
            ds = file.ds.sel(lat=region.lat, lon=region.lon, method='nearest')

        else:
            ds = file.ds.mean(dim=('lat', 'lon'))

        self.write_csv(ds, attrs, csv_path, first_file=(file.index == 0))
