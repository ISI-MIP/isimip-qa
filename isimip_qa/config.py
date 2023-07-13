from collections import defaultdict
from datetime import datetime
from itertools import product
from pathlib import Path

from isimip_utils.config import Settings as BaseSettings
from isimip_utils.decorators import cached_property
from isimip_utils.fetch import (fetch_definitions, fetch_pattern, fetch_schema,
                                fetch_tree)


class Settings(BaseSettings):

    def setup(self, args):
        super().setup(args)

        # create a dict to store masks
        self.MASKS = {}

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
                placeholders = {key: value for key, value in zip(self.PLACEHOLDERS.keys(), permutations)}
                path_str = str(self.PATH).format(**placeholders)
                path = Path(path_str)
                path = path.parent / path.name.lower()  # ensure that the name of the path is lower case
                primary = bool(set(permutations).intersection(settings.PRIMARY)) if settings.PRIMARY else True
                datasets.append((path, primary))

            return datasets
        else:
            return [(self.PATH, True)]

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
    def ASSESSMENTS_NAME(self):
        placeholders = {}
        for placeholder, values in self.PLACEHOLDERS.items():
            primary_values = [value for value in values if value in self.PRIMARY] if self.PRIMARY else []
            if primary_values:
                values_strings = primary_values
            elif len(values) < 10:
                values_strings = values
            else:
                values_strings = ['various']
            placeholders[placeholder] = '+'.join(values_strings).lower()

        return self.PATH.name.format(**placeholders)

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
        return self.args.get('PRIMARY').split(',')

    @cached_property
    def TIMES(self):
        return sorted([self.parse_time(time) for time in self.args.get('TIMES', '').split(',')])

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

    def parse_time(self, time):
        try:
            datetime.strptime(time, '%Y-%m-%d')
        except ValueError:
            try:
                datetime.strptime(time, '%Y')
            except ValueError:
                self.parser.error('TIMES need to provided as "%Y-%m-%d" or "%Y".')

        return time


settings = Settings()
