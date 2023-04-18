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

        if settings.TIMES is None:
            # get first time of the first dataset
            times = [str(file.ds.time.isel(time=0).dt.strftime('%Y-%m-%d').data)]

            # only process the first file if TIMES was not set
            if not file.first:
                return
        else:
            times = settings.TIMES

        for time_index, time in enumerate(times):
            try:
                ds = file.ds.sel(time=[time])
            except KeyError:
                # continue it the time was not found in the dataset
                continue
            else:
                if region.type == 'mask':
                    ds = ds.where(region.mask == 1)

                # write if any data was found in this dataset
                self.write(ds, path, first=(time_index == 0))
