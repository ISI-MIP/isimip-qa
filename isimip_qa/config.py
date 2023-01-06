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

        self.DATASET_PATHS = []
        if self.SPECIFIERS:
            # create lists of the form [[(identifier, specifier1), (identifier, specifier2), ...], ...]
            specifier_lists = []
            for identifier, specifiers in self.SPECIFIERS.items():
                specifier_lists.append([(identifier, specifier) for specifier in specifiers])

            # create a cartesian product of those lists
            specifier_product = [dict(item) for item in product(*specifier_lists)]

            # create dataset path for each item in the product
            for specifier_dict in specifier_product:
                path_str = str(self.PATH).format(**specifier_dict)
                path = Path(path_str)
                path = path.parent / path.name.lower()  # ensure that the name of the path is lower case
                self.DATASET_PATHS.append(path)
        else:
            self.DATASET_PATHS.append(self.PATH)

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
