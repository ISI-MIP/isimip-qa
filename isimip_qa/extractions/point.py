import logging

import xarray as xr

from ..config import settings
from ..models import Extraction

logger = logging.getLogger(__name__)


class PointExtraction(Extraction):

    def __init__(self, dataset, points):
        super().__init__(dataset)
        self.points = points

    @property
    def is_complete(self):
        return all([self.get_csv_path(place).exists() for place, lat, lon in self.points])

    def run(self):
        for file_path in self.dataset.files:
            logger.info(f'load {file_path}')
            ds = xr.load_dataset(file_path)
            for place, lat, lon in self.points:
                csv_path = self.get_csv_path(place)
                logger.info(f'extract to {csv_path}')

                df = ds.sel(lat=lat, lon=lon, method='nearest').to_dataframe()

                if csv_path.exists():
                    df.to_csv(csv_path, mode='a', header=False)
                else:
                    csv_path.parent.mkdir(exist_ok=True, parents=True)
                    df.to_csv(csv_path)

    def get_csv_path(self, place):
        region = self.dataset.specifiers['region']
        path_str = str(self.dataset.path).replace(f'_{region}_', f'_{place}_')
        return settings.EXTRACTIONS_PATH.joinpath(path_str).with_suffix('.csv')
