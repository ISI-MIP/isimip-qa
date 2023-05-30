from collections import defaultdict
from datetime import datetime
from itertools import product
from pathlib import Path

from isimip_utils.config import ISIMIPSettings
from isimip_utils.decorators import cached_property
from isimip_utils.exceptions import DidNotMatch
from isimip_utils.fetch import (fetch_definitions, fetch_pattern,
                                fetch_schema, fetch_tree)


class Settings(ISIMIPSettings):

    def setup(self, parser):
        # import here to prevent circular inclusion
        from .assessments import assessment_classes
        from .extractions import extraction_classes
        from .regions import regions
        from .models import Region

        super().setup(parser)
        if self.DATASETS_PATH is None:
            self.DATASETS_PATH = Path.cwd()
        if self.EXTRACTIONS_PATH is None:
            self.EXTRACTIONS_PATH = Path.cwd()
        if self.ASSESSMENTS_PATH is None:
            self.ASSESSMENTS_PATH = Path.cwd()

        self.PATH = Path(settings.PATH).expanduser()
        self.DATASETS_PATH = Path(settings.DATASETS_PATH).expanduser()
        self.EXTRACTIONS_PATH = Path(settings.EXTRACTIONS_PATH).expanduser()
        self.ASSESSMENTS_PATH = Path(settings.ASSESSMENTS_PATH).expanduser()

        # create a dict to store masks
        settings.MASKS = {}

        # setup times
        if self.TIMES:
            self.TIMES = sorted([self.parse_time(time) for time in self.TIMES.split(',')])

        # setup params
        placeholders_dict = defaultdict(list)
        for placeholders_string in self.PLACEHOLDERS:
            placeholder, values = placeholders_string.split('=')
            placeholders_dict[placeholder] += values.split(',')
        self.PLACEHOLDERS = placeholders_dict

        # setup regions
        if self.REGIONS is None:
            self.REGIONS = 'global'
        self.REGIONS = [
            Region(region) for region in regions
            if region.get('specifier') in (
                self.REGIONS.split(',') if (self.REGIONS is not None) else ['global']
            )
        ]

        # setup extractions
        if self.EXTRACTIONS is None:
            self.EXTRACTIONS = [extraction_class() for extraction_class in extraction_classes]
        else:
            self.EXTRACTIONS = [
                extraction_class() for extraction_class in extraction_classes
                if extraction_class.specifier in self.EXTRACTIONS.split(',')
            ]

        # setup assessments
        if self.ASSESSMENTS is None:
            self.ASSESSMENTS = [assessment_class() for assessment_class in assessment_classes]
        else:
            self.ASSESSMENTS = [
                assessment_class() for assessment_class in assessment_classes
                if assessment_class.specifier in self.ASSESSMENTS.split(',')
            ]

        # setup color
        if self.PRIMARY is not None:
            self.PRIMARY = set(self.PRIMARY.split(','))

    @cached_property
    def PERMUTATIONS(self):
        return list(product(*self.PLACEHOLDERS.values()))

    @cached_property
    def DATASETS(self):
        from .models import Dataset

        if self.PLACEHOLDERS:
            datasets = []

            for permutations in self.PERMUTATIONS:
                placeholders = {key: value for key, value in zip(self.PLACEHOLDERS.keys(), permutations)}
                path_str = str(self.PATH).format(**placeholders)
                path = Path(path_str)
                path = path.parent / path.name.lower()  # ensure that the name of the path is lower case

                try:
                    datasets.append(Dataset(path))
                except DidNotMatch as e:
                    self.parser.error(e)

            return datasets
        else:
            try:
                return [Dataset(self.PATH)]
            except DidNotMatch as e:
                self.parser.error(e)

    @cached_property
    def PRIMARY_DATASETS(self):
        if self.PRIMARY is None:
            return self.DATASETS
        else:
            return [
                self.DATASETS[index] for index, permutation in enumerate(self.PERMUTATIONS)
                if set(permutation).intersection(self.PRIMARY)
            ]

    @cached_property
    def DEFINITIONS(self):
        assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'
        return fetch_definitions(self.PROTOCOL_LOCATIONS.split(), self.PATH)

    @cached_property
    def PATTERN(self):
        assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'
        return fetch_pattern(self.PROTOCOL_LOCATIONS.split(), self.PATH)

    @cached_property
    def SCHEMA(self):
        assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'
        return fetch_schema(self.PROTOCOL_LOCATIONS.split(), self.PATH)

    @cached_property
    def TREE(self):
        assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'
        return fetch_tree(self.PROTOCOL_LOCATIONS.split(), self.PATH)

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
