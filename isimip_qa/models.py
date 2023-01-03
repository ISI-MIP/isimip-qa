from isimip_utils.decorators import cached_property
from isimip_utils.patterns import match_dataset_path


class Dataset(object):

    def __init__(self, dataset_path, pattern, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.dataset_path, self.specifiers = match_dataset_path(pattern, dataset_path)

    @cached_property
    def files(self):
        path = self.input_path / self.dataset_path
        glob = path.parent.glob(f'{path.stem}*')
        return sorted(glob)
