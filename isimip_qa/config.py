from collections import defaultdict
from itertools import product
from pathlib import Path

from isimip_utils.config import ISIMIPSettings
from isimip_utils.decorators import cached_property
from isimip_utils.fetch import (fetch_definitions, fetch_pattern,
                                fetch_schema, fetch_tree)


class Settings(ISIMIPSettings):

    def setup(self, parser):
        super().setup(parser)
        self.PATH = Path(settings.PATH)
        self.DATASETS_PATH = Path(settings.DATASETS_PATH)
        self.EXTRACTIONS_PATH = Path(settings.EXTRACTIONS_PATH)
        self.ASSESSMENTS_PATH = Path(settings.ASSESSMENTS_PATH)
        self.PROTOCOL_PATH = Path(*self.PATH.parts[:3])

        specifiers_dict = defaultdict(list)
        for specifier_string in self.SPECIFIERS:
            identifier, specifiers = specifier_string.split('=')
            specifiers_dict[identifier] += specifiers.split(',')
        self.SPECIFIERS = specifiers_dict
        self.IDENTIFIERS = list(self.SPECIFIERS.keys())

    @cached_property
    def DATASETS(self):
        datasets = []
        for permutations in self.PERMUTATIONS:
            specifiers = {key: value for key, value in zip(self.SPECIFIERS.keys(), permutations)}
            path_str = str(self.PATH).format(**specifiers)
            path = Path(path_str)
            path = path.parent / path.name.lower()  # ensure that the name of the path is lower case
            datasets.append(path)
        return datasets

    @cached_property
    def PERMUTATIONS(self):
        return list(product(*self.SPECIFIERS.values()))

    @cached_property
    def DEFINITIONS(self):
        assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'
        return fetch_definitions(self.PROTOCOL_LOCATIONS.split(), self.PROTOCOL_PATH)

    @cached_property
    def PATTERN(self):
        assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'
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
