from collections import defaultdict
from itertools import product
from pathlib import Path

from isimip_utils.config import Settings as BaseSettings
from isimip_utils.decorators import cached_property
from isimip_utils.fetch import fetch_definitions, fetch_pattern, fetch_schema, fetch_tree


class Settings(BaseSettings):

    def setup(self, args):
        super().setup(args)

        # create a dict to store masks
        self.MASKS = {}

        # check if all placeholders are there
        if self.PATH and self.PLACEHOLDERS:
            permutations = next(product(*self.PLACEHOLDERS.values()))
            placeholders = dict(zip(self.PLACEHOLDERS.keys(), permutations))

            try:
                str(self.PATH).format(**placeholders)
            except KeyError as e:
                raise RuntimeError('Some of the placeholders are missing.') from e

    @cached_property
    def PATH(self):
        return Path(self.args['PATH']).expanduser()

    @cached_property
    def PLACEHOLDERS(self):
        placeholders_dict = defaultdict(list)
        for placeholders_string in self.args.get('PLACEHOLDERS'):
            placeholder, values = placeholders_string.split('=')
            placeholders_dict[placeholder] += values.split(',')
        return placeholders_dict

    @cached_property
    def DATASETS(self):
        if self.PLACEHOLDERS:
            datasets = []
            placeholder_permutations = list(product(*self.PLACEHOLDERS.values()))
            for permutations in placeholder_permutations:
                placeholders = dict(zip(self.PLACEHOLDERS.keys(), permutations))
                path_str = str(self.PATH).format(**placeholders)
                path = Path(path_str)
                path = path.parent / path.name.lower()  # ensure that the name of the path is lower case
                datasets.append(path)

            return datasets
        else:
            return [self.PATH]

    @cached_property
    def PROTOCOL_PATH(self):
        try:
            return Path(self.args['PROTOCOL_PATH']).expanduser()
        except KeyError:
            return self.PATH

    @cached_property
    def DATASETS_PATH(self):
        return Path(self.args['DATASETS_PATH']).expanduser()

    @cached_property
    def EXTRACTIONS_PATH(self):
        return Path(self.args['EXTRACTIONS_PATH']).expanduser()

    @cached_property
    def ASSESSMENTS_PATH(self):
        return Path(self.args['ASSESSMENTS_PATH']).expanduser()

    @cached_property
    def REGIONS(self):
        return self.args.get('REGIONS').split(',')

    @cached_property
    def EXTRACTIONS(self):
        return self.args.get('EXTRACTIONS').split(',')

    @cached_property
    def ASSESSMENTS(self):
        return self.args.get('ASSESSMENTS').split(',')

    @cached_property
    def PRIMARY(self):
        return self.args.get('PRIMARY').split(',') if self.args.get('PRIMARY') else []

    @cached_property
    def EXTRACTIONS_LOCATIONS(self):
        return self.args.get('EXTRACTIONS_LOCATIONS').split()

    @cached_property
    def DEFINITIONS(self):
        assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'
        return fetch_definitions(self.PROTOCOL_LOCATIONS.split(), self.PROTOCOL_PATH)

    @cached_property
    def PATTERN(self):
        return fetch_pattern(self.PROTOCOL_LOCATIONS.split(), self.PROTOCOL_PATH)

    @cached_property
    def SCHEMA(self):
        assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'
        return fetch_schema(self.PROTOCOL_LOCATIONS.split(), self.PROTOCOL_PATH)

    @cached_property
    def TREE(self):
        assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'
        return fetch_tree(self.PROTOCOL_LOCATIONS.split(), self.PROTOCOL_PATH)


settings = Settings()
