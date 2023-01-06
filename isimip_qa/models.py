from isimip_utils.decorators import cached_property
from isimip_utils.patterns import match_dataset_path

from .config import settings


class Dataset(object):

    def __init__(self, dataset_path):
        self.path, self.specifiers = match_dataset_path(settings.PATTERN, dataset_path)

    @cached_property
    def files(self):
        path = settings.DATASETS_PATH / self.path
        glob = path.parent.glob(f'{path.stem}*')
        return sorted(glob)


class Assessment(object):

    def __init__(self, dataset):
        self.dataset = dataset

    def plot(self):
        raise NotImplementedError


class Extraction(object):

    def __init__(self, dataset):
        self.dataset = dataset

    @property
    def is_complete(self):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError
