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

    def replace_name(self, **specifiers):
        name = self.path.name
        for identifier, specifiers in specifiers.items():
            old = self.specifiers[identifier]
            new = '+'.join(specifiers) if isinstance(specifiers, list) else specifiers
            name = name.replace(old.lower(), new.lower())
        return self.path.parent / name


class Assessment(object):

    extraction_classes = []

    def extract(self, datasets):
        for dataset in datasets:
            for extraction_class in self.extraction_classes:
                extraction_class().extract(dataset)

    def plot(self, datasets):
        raise NotImplementedError


class Extraction(object):

    def extract(self, dataset):
        raise NotImplementedError
