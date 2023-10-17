import logging

from ..mixins import JSONExtractionMixin, RemoteExtractionMixin
from ..models import Extraction

logger = logging.getLogger(__name__)


class AttrsExtraction(JSONExtractionMixin, RemoteExtractionMixin, Extraction):

    specifier = 'attrs'
    region_types = ['global', 'mask', 'point']

    def extract(self, file):
        if file.first:
            logger.info(f'extract {self.region.specifier} {self.specifier} from {file.path}')

            var = next(iter(file.ds.data_vars.values()))
            attrs = var.attrs

            logger.info(f'write {self.path}')
            self.write(attrs)
