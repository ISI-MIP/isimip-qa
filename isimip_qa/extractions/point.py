import logging

import xarray as xr

from ..config import settings
from ..constants import points
from ..models import Extraction

logger = logging.getLogger(__name__)


class PointExtraction(Extraction):

    def extract(self, dataset):
        if all([self.get_path(dataset, place).exists() for place, lat, lon in points]):
            return

        for file_path in dataset.files:
            logger.info(f'load {file_path}')
            ds = xr.load_dataset(file_path)
            for place, lat, lon in points:
                csv_path = self.get_path(dataset, place)
                logger.info(f'extract to {csv_path}')

                df = ds.sel(lat=lat, lon=lon, method='nearest').to_dataframe()

                if csv_path.exists():
                    df.to_csv(csv_path, mode='a', header=False)
                else:
                    csv_path.parent.mkdir(exist_ok=True, parents=True)
                    df.to_csv(csv_path)

    def get_path(self, dataset, place):
        path = dataset.replace_name(region=place)
        return settings.EXTRACTIONS_PATH.joinpath(path).with_suffix('.csv')
