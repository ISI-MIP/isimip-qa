from isimip_utils.decorators import cached_property
from isimip_utils.patterns import match_dataset_path


class Dataset(object):

    def __init__(self, pattern, dataset_path, input_path, output_path):
        self.path, self.specifiers = match_dataset_path(pattern, dataset_path)
        self.input_path = input_path
        self.output_path = output_path

    @cached_property
    def files(self):
        path = self.input_path / self.path
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

    def extract(self):
        raise NotImplementedError
