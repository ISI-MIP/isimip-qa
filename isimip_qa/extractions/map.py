import logging

from ..config import settings
from ..mixins import CSVExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class MapExtraction(CSVExtractionMixin, Extraction):

    specifier = 'map'
    region_types = ['global', 'mask']

    def extract(self, dataset, region, file):
        path = self.get_path(dataset, region)
        logger.info(f'extract to {path}')

        # only process the first file if TIMES is not set
        if settings.TIMES is None and not file.first:
            return

        if region.type == 'mask':
            ds = file.ds.where(region.mask == 1)
        else:
            ds = file.ds

        if settings.TIMES is None:
            ds_time = ds.isel(time=slice(0, 1))
            self.write(ds_time, path, first=True)
        else:
            for time_index, time in enumerate(settings.TIMES):
                ds_time = ds.sel(time=time)

                # the first time we write is if time_index is and the dataset
                # is not empty (does not need to happen on the first file)
                first = time_index == 0 and ds_time.time.size > 0
                self.write(ds_time, path, first=first)
