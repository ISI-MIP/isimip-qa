import logging

from ..mixins import CSVExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class MaskExtraction(CSVExtractionMixin, Extraction):

    region_types = ['mask']

    def extract(self, dataset, region, ds):
        csv_path = self.get_path(dataset, region)
        logger.info(f'extract to {csv_path}')

        df = ds.where(region.mask == 1).mean(dim=('lat', 'lon')).to_dataframe()

        self.write_csv(df, csv_path)
