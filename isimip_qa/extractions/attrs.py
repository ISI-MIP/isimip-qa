import logging

from ..mixins import JSONExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class AttrsExtraction(JSONExtractionMixin, Extraction):

    specifier = 'attrs'
    region_types = ['global', 'mask', 'point']

    def extract(self, dataset, region, file):
        if file.first:
            path = self.get_path(dataset, region)
            logger.info(f'extract to {path}')

            var = next(iter(file.ds.data_vars.values()))
            attrs = var.attrs

            self.write(attrs, path)
