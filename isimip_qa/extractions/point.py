import logging

from ..mixins import CSVExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class PointExtraction(CSVExtractionMixin, Extraction):

    region_types = ['point']

    def extract(self, dataset, region, ds):
        csv_path = self.get_path(dataset, region)
        logger.info(f'extract to {csv_path}')

        df = ds.sel(lat=region.lat, lon=region.lon, method='nearest').to_dataframe()

        self.write_csv(df, csv_path)
