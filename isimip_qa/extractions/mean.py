import logging

from ..mixins import CSVExtractionMixin, RemoteExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class MeanExtraction(CSVExtractionMixin, RemoteExtractionMixin, Extraction):

    specifier = 'mean'
    region_types = ['global', 'mask', 'point']

    def extract(self, dataset, region, file):
        logger.info(f'extract {region.specifier} {self.specifier} from {file.path}')

        if region.type == 'mask':
            ds = file.ds.where(region.mask == 1).mean(dim=('lat', 'lon'), skipna=True)

        elif region.type == 'point':
            ds = file.ds.sel(lat=region.lat, lon=region.lon, method='nearest')

        else:
            ds = file.ds.mean(dim=('lat', 'lon'), skipna=True)

        path = self.get_path(dataset, region)
        logger.info(f'write {path}')
        self.write(ds, path, first=file.first)
